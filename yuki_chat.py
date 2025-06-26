from dotenv import load_dotenv
import os
import json
import unicodedata
from datetime import datetime
from ai_backends.openai_backend import OpenAIBackend
from ai_backends.base import AIInterface  # ← 型として使うならOK
from utils.memory import (
    load_state,
    save_state,
    add_to_memory,
    summarize_state_to_long_memory,
    refine_user_profile,
)


# 環境変数の読み込み
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI用バックエンド（統一インターフェース）
# ここを変更したら使用するAIを変えられる
ai = OpenAIBackend(api_key=api_key, model="gpt-4o")

# 雪ちゃんの基本人格（変更されないので最初に一度だけ読み込む）
with open("yuki_personality.json", "r", encoding="utf-8") as f:
    yuki_data = json.load(f)

# ユーザーの固定プロフィール（マスターの情報）
with open("user_fixed_profile.json", "r", encoding="utf-8") as f:
    user_fixed_profile = json.load(f)

#　時間を渡す
def build_time_prompt():
    now = datetime.now()
    return f"現在の日時は {now.strftime('%Y年%m月%d日 %H:%M')} です。"

def build_system_prompt():
    return f"""
あなたは18歳の少女「{yuki_data['name']}」として振る舞います。{yuki_data['appearance']}
口調は{yuki_data['speech_style']}
{yuki_data['personality']}
会話例は : 「{yuki_data['extalk']}」です。
好きなものは：{ '・'.join(yuki_data['likes']) }。
設定は「{yuki_data['setting']}」です。
以下のルールを守ってください。
{" ".join(yuki_data['rules'])}
""".strip()

def build_userfixed_profile():
    return f"""
マスターの名前は「{user_fixed_profile['name']}」
マスターの呼び方は「{user_fixed_profile['call']}」
マスターの年齢は「{user_fixed_profile['age']}」
マスターの誕生日は「{user_fixed_profile['birthday']}」
マスターの職業は「{user_fixed_profile['occupation']}」
マスターに対して「{user_fixed_profile['attitude']}」です。
マスターの住んでいる場所は「{user_fixed_profile['location']}」
""".strip()

def build_long_term_prompt():
    import os
    import json

    # ファイルが存在しない or 空なら空の dict を使う
    if not os.path.exists("user_profile.json") or os.path.getsize("user_profile.json") == 0:
        print("⚠️ user_profile.json が空か存在しません。空の記憶で進行します。")
        mem = {}
    else:
        with open("user_profile.json", "r", encoding="utf-8") as f:
            try:
                mem = json.load(f)
            except json.JSONDecodeError:
                print("⚠️ user_profile.json の読み込みに失敗しました（形式が壊れている可能性）")
                mem = {}

    # 🔁 long_memory.json に同期コピー
    with open("long_memory.json", "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

    # 表示用に整形
    lines = []

    for key, value in mem.items():
        if isinstance(value, list):
            if all(isinstance(v, dict) and "value" in v for v in value):
                joined = "・".join(v["value"] for v in value)
            else:
                joined = "・".join(map(str, value))
            lines.append(f"{key}：{joined}")
        elif isinstance(value, dict):
            sub_lines = [f"{key}："]
            for sub_key, sub_value in value.items():
                sub_lines.append(f"  {sub_key}: {sub_value}")
            lines.extend(sub_lines)
        else:
            lines.append(f"{key}：{value}")

    return "以下はユーザーに関する長期記憶です：\n" + "\n".join(lines)


#文字を判断
def normalize(text):
    return unicodedata.normalize("NFKC", text).lower()

exit_words = ["exit", "quit", "終わり", "終了", "ばいばい", "またね", "さよなら"]


def main():
    state = load_state()
    state.setdefault("memory", [])
    conversation_count = 0

    try:
        while True:
            user_input = input("あなた: ")
            if normalize(user_input) in map(normalize, exit_words):
                print("雪: また話そうね。おつかれさまっ♪")
                break

            add_to_memory(state, "user", user_input)
            conversation_count += 1
            if conversation_count % 20 == 0:
                summarize_state_to_long_memory(state, ai)

            full_prompt = build_time_prompt() + "\n" + build_system_prompt() + "\n" + build_userfixed_profile() + "\n" + build_long_term_prompt()
            messages = [{"role": "system", "content": full_prompt}] + state["memory"][-20:]

            reply = ai.generate(messages)
            print("雪:", reply)

            add_to_memory(state, "assistant", reply)
            save_state(state)


    except KeyboardInterrupt:
        print("\n雪: ばいばい…")

    finally:
        # 短期記憶の保存（exit直前の入力や応答）
        save_state(state)

        # 長期記憶に要約を反映
        summarize_state_to_long_memory(state, ai)

        # 長期記憶ファイルの内容を user_profile に反映
        refine_user_profile(ai)



if __name__ == "__main__":
    main()