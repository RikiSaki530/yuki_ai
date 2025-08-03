import json
import os
from dotenv import load_dotenv
from datetime import datetime
from ai_backends.llama_backend import LlamaBackend 
from ai_backends.openai_backend import OpenAIBackend # OpenAI用バックエンド

from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

STATE_PATH = os.path.join("talk_memory", "state.json")
EPISODE_MEMORY_PATH = os.path.join("user_memory", "episode_memory.json")


"""
ここの処理は,llama3を用いて処理しようかな。
"""

# Llama用バックエンド（統一インターフェース）
#ai = LlamaBackend(model="llama3")

# OpenAI用バックエンド（統一インターフェース）
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
ai = OpenAIBackend(api_key=api_key, model="gpt-3.5-turbo")

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
    

# 会話履歴からタグを抽出→比較まで
def pic_episode_memory():

    episode_memory_prompt = []

    """
    talk_memory/state.json からエピソード記憶を抽出して episode_memory.jsonと比較 。
    使えそうなエピソードがあれば提供。
    """

    # 最新10件の会話を取得
    recent_conversations = load_recent_conversation(6) 
    # 会話履歴の文字列生成（role: content 形式）
    history = "\n".join([f"{m['role']}: {m['content']}" for m in recent_conversations])


    if not recent_conversations:
        print("⚠️ 会話履歴がありません。")
        return

    prompt = '''
    以下のエピソードは,ユーザと雪ちゃんの会話ログです。
    この履歴から、意味のある「タグ」を最大10個まで抽出してください。

    条件：
    - タグは日本語で返してください。
    - タグは短い単語が望ましい。
    - もし抽出できなければ、空のリストを返してください。推測で埋めないでください。
    - タグにする単語は,自由に作成してください。
    - 出力形式はJSONのリストとして返してください（例: ["紅茶", "秋", "星空"]）。
    - **Markdownのコード囲い（```）やコメントは含めないでください。**
    
    会話ログ：
    {history}
    '''.format(history = history)

    result = ai.generate([
            {"role": "system", "content": "あなたはユーザー情報を抽出するアシスタントです"},
            {"role": "user", "content": prompt}
    ])

    try:
        result = json.loads(result) if isinstance(result, str) else result
    except json.JSONDecodeError:
        print("⚠️ タグの抽出に失敗しました。JSON形式が正しくありません。")
        result = []

    try:
        episode_memory_prompt = compare_tags_with_episode_memory(result, threshold=0.8)  # 抽出したタグとエピソード記憶を比較
        if not episode_memory_prompt:
            print(result)
            print("⚠️ 抽出されたタグがエピソード記憶と一致しませんでした。")
        else:
            print("✅ 抽出されたタグ:", result)
            
    except json.JSONDecodeError:
        print("⚠️ タグの抽出に失敗しました。JSON形式が正しくありません。")
        episode_memory_prompt = []  

    # 最後の return を以下に変更する
    if episode_memory_prompt:
        memory_text = "\n".join(
            f"＜記憶＞ {ep.get('会話要約', '')}（タグ: {', '.join(ep.get('タグ', []))}）"
            for ep in episode_memory_prompt
        )
        return json.dumps({"episode": memory_text}, ensure_ascii=False)
    else:
        return ""
        

# 抽出したタグとエピソード記憶のタグを比較
def compare_tags_with_episode_memory(tags, threshold=0.8):

    episode_memory_prompt = []

    if not os.path.exists(EPISODE_MEMORY_PATH):
        print(f"⚠️ ファイルが存在しません: {EPISODE_MEMORY_PATH}")
        return []
    
    with open(EPISODE_MEMORY_PATH, "r", encoding="utf-8") as f:
        try:
            episode_memory = json.load(f)
            if not isinstance(episode_memory, list):
                episode_memory = []
        except json.JSONDecodeError:
            print("⚠️ episode_memory.json の読み込みに失敗しました（形式エラー）。")
            episode_memory = []

    # ✅ 事前にすべての比較タグをベクトル化
    tag_embeddings = {tag: model.encode(tag, convert_to_tensor=True) for tag in tags}

    for episode in episode_memory:
        memoryscore = 0
        episode_tags = episode.get("タグ", [])

        # ✅ 各エピソードタグも1回だけエンコード
        episode_embeddings = {et: model.encode(et, convert_to_tensor=True) for et in episode_tags}

        # ✅ 類似度判定（全タグ同士で1回ずつ）
        for episode_tag, ep_emb in episode_embeddings.items():
            for tag, tag_emb in tag_embeddings.items():
                score = util.cos_sim(tag_emb, ep_emb).item()
                if score >= threshold:
                    memoryscore += 1
                    break  # この episode_tag については一致と見なす

        memoryscore += episode.get("スコア", 0)

        if memoryscore > 8:
            episode_memory_prompt.append(episode)

    return episode_memory_prompt



def is_similar_tag(tag1, tag2, threshold=0.8):
    emb1 = model.encode(tag1, convert_to_tensor=True)
    emb2 = model.encode(tag2, convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2).item()
    return score >= threshold

