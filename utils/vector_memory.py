import chromadb
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

from ai_backends.openai_backend import OpenAIBackend # OpenAI用バックエンド
STATE_PATH = os.path.join("talk_memory", "state.json")
EPISODE_MEMORY_PATH = os.path.join("user_memory", "episode_memory.json")

client_chroma = chromadb.PersistentClient(path="yuki_memory_db")
collection = client_chroma.get_or_create_collection("long_memory")

# OpenAI用バックエンド（統一インターフェース）
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
ai = OpenAIBackend(api_key=api_key, model="gpt-4o-mini")


def get_embedding(text: str) -> list[float]:
    return ai.embedding(
        input=text,
        model="text-embedding-3-small"
    ).data[0].embedding

def save_long_memory(text: str, metadata: dict, id: str):
    embedding = get_embedding(text)
    collection.add(
        ids=[id],
        documents=[text],
        embeddings=[embedding],
        metadatas=[metadata]
    )


def search_memory(query_text: str, n_results: int = 3):
    query_vec = get_embedding(query_text)
    results = collection.query(query_embeddings=[query_vec], n_results=n_results)
    return results


# 会話履歴を読み込む
def load_recent_conversation(n):
    """
    talk_memory/state.json から最新 n 件の会話を取り出す（引数に path を含まない）
    """
    if not os.path.exists(STATE_PATH):
        print(f"⚠️ ファイルが存在しません: {STATE_PATH}")
        return []

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

        memory = data.get("memory", [])
        if not isinstance(memory, list):
            print("⚠️ 'memory' フィールドがリストではありません。")
            return []

        return memory[-n:]  # 最新 n 件を取得

# Chromaから意味的に近い記憶を抽出する関数
def get_relevant_memories(user_input: str, threshold: float = 0.25, n_results: int = 5) -> list[dict]:
    """
    ユーザー入力から意味的に近い記憶をChromaから抽出する。
    閾値以下の距離のみを返す。

    Returns:
        List[dict] 形式の記憶（text, metadata, distance）
    """
    query_vec = get_embedding(user_input)
    results = collection.query(query_embeddings=[query_vec], n_results=n_results)

    relevant = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        if dist <= threshold:
            relevant.append({
                "text": doc,
                "metadata": meta,
                "distance": dist
            })
    return relevant


# --- 追加: 全件エクスポート ---
def export_all_memories() -> list[dict]:
    """
    Chromaに保存されているすべての記憶を取得（デバッグ・可視化用）
    """
    all = collection.peek()
    return [
        {"text": doc, "metadata": meta}
        for doc, meta in zip(all["documents"], all["metadatas"])
    ]


# 自動で会話履歴を読み取り → タグ抽出 → 類似記憶をChromaから取得
def auto_extract_relevant_memories(n_turns: int = 5, threshold: float = 0.25 ) -> list[dict]:
    
    conversation_text = load_recent_conversation(5)
    history = "\n".join([f"{m['role']}: {m['content']}" for m in conversation_text])

    tag_prompt = f"""以下の会話ログから、意味的に重要なキーワード（3〜5語）を抽出してください。
出力形式はJSONのリストとし、単語だけを含めてください（例: ["紅茶", "星空", "旅行"]）。
Markdownの囲いや説明文は禁止です。

会話ログ:
{history}
"""

    tag_result = ai.generate(
        messages=[
            {"role": "system", "content": "あなたは重要な語を抽出する日本語アシスタントです。"},
            {"role": "user", "content": tag_prompt}
        ]
    )

    try:
        print(tag_result)
        tags = json.loads(tag_result)

        all_hits = []
        for tag in tags:
            vec = get_embedding(tag)
            results = collection.query(query_embeddings=[vec], n_results=5)
            for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
                if dist <= threshold:
                    all_hits.append({
                        "text": doc,
                        "metadata": meta,
                        "distance": dist
                    })
        return json.dumps({"semantic": all_hits}, ensure_ascii=False)
    except Exception as e:
        print("⚠️ :", e)
        return ""