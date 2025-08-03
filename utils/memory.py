import json
import os
from dotenv import load_dotenv
from datetime import datetime
from utils.vector_memory import save_long_memory, load_recent_conversation

STATE_PATH = os.path.join("talk_memory", "state.json")
USER_MEMORY_PATH = os.path.join("talk_memory", "user_memory.json")
USER_PROFILE_PATH = os.path.join("user_memory", "user_profile.json")

# ディレクトリ設定
today_str = datetime.now().strftime("%Y-%m-%d")
base_dir = "days_log"
filename = f"episode_{today_str}.json"
DAY_STATE_PATH = os.path.join(base_dir, filename)




#読み込み
def load_state():
    if not os.path.exists(STATE_PATH):
        return {"memory": [], "user_name": "", "last_topic": ""}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


#stateセーブ
def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


#stateとは別に会話ログを保存
def day_save_state(entry, path=DAY_STATE_PATH):

    # entry は {"role": "user", "content": "..."} の形式を想定
    if not isinstance(entry, dict) or "role" not in entry or "content" not in entry:
        return

    # timestamp を追加（"HH:MM:SS" の形式）
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.now().strftime("%H:%M:%S")

    # 既存データの読み込み（あれば）
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
        except json.JSONDecodeError:
            history = []
    else:
        history = []

    # 1件追加
    history.append(entry)

    # 保存
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


#stateやday_logに会話を保存
def add_to_memory(state, role, content):
    entry = {"role": role, "content": content}
    state.setdefault("memory", [])
    state["memory"].append(entry)

    if len(state["memory"]) > 20:
        state["memory"] = state["memory"][-20:]

    # ✅ 1件ずつファイルに追記保存
    day_save_state(entry)


#dict型の再起的マージ
def recursive_merge_dict(a, b):
    for key, value in b.items():
        if key in a and isinstance(a[key], dict) and isinstance(value, dict):
            recursive_merge_dict(a[key], value)
        else:
            a[key] = value


def summarize_state_to_chroma(ai):
    history = load_recent_conversation(20)

    prompt = f"""以下はAIとユーザーの会話ログです。この情報から「人物プロファイル情報」を抽出してください。

出力形式は以下のテンプレートに従ってください。未使用項目は空欄またはnullでも構いません。
Markdownのコード囲い（```）やコメントは禁止。JSON本体のみ返してください。
scoreは1〜10の整数で、重要度を示します。

テンプレート:
{{
    "好きなこと": [{{"value": "紅茶", "score": 4}}],
    "嫌いなこと": [{{"value": "ゴーヤ", "score": 5}}],
    "得意なこと": [{{"value": "プログラミング", "score": 5}}],
    "苦手なこと": [{{"value": "早起き", "score": 3}}],
    "将来の夢": [{{"value": "AIで世界を変える", "score": 6}}],
    "気になること": [{{"value": "言語モデル", "score": 4}}],
    "大事にしたいこと": [{{"value": "やさしさ", "score": 5}}]
}}


会話ログ：
{history}
"""

    result = ai.generate([
        {"role": "system", "content": "あなたはユーザー情報を抽出するアシスタントです"},
        {"role": "user", "content": prompt}
    ])

    try:
        memory_data = json.loads(result)

        for category, items in memory_data.items():
            if isinstance(items, list):
                for i, item in enumerate(items):
                    if not isinstance(item, dict):
                        continue
                    value = item.get("value", "")
                    score = item.get("score", 1)
                    if not value:
                        continue
                    save_long_memory(
                        text=value,
                        metadata={
                            "category": category,
                            "score": score,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "source": "state_summary"
                        },
                        id=f"{category}_{i}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    )

        print("✅ 会話内容をChromaへ保存しました。")

    except Exception as e:
        print("⚠️ JSON変換に失敗しました:", e)
        print("返答:", result)