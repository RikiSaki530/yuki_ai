from dotenv import load_dotenv
import os
import json
import unicodedata
from datetime import datetime
from ai_backends.openai_backend import OpenAIBackend # OpenAI用バックエンド
from ai_backends.llama_backend import LlamaBackend 
from ai_backends.base import AIInterface  # ← 型として使うならOK
from interaction.self_talker import SelfTalker
#from braina.router import route_context



from yuki_chat_threaded import run_chat

from utils.vector_memory import (
    auto_extract_relevant_memories
)


from utils.memory import (
    load_state,
    save_state,
    add_to_memory,
    summarize_state_to_chroma,
)

from utils.episode_memory import (
    pic_episode_memory
)

#Yukiちゃんの情報の呼び出し
YUKI_PERSONALITY_PATH = os.path.join("Yuki_memory", "yuki_personality.json")

#user情報の呼び出し
USER_FIXED_PROFILE_PATH = os.path.join("user_memory", "user_fixed_profile.json")
USER_PROFILE_PATH = os.path.join("user_memory", "user_profile.json")

#会話用のjsonファイルの呼び出し
STATE_PATH = os.path.join("talk_memory", "state.json")
USER_MEMORY_PATH = os.path.join("talk_memory", "user_memory.json")


# 環境変数の読み込み
load_dotenv()

# OpenAI用バックエンド（統一インターフェース）

api_key = os.getenv("OPENAI_API_KEY")
ai = OpenAIBackend(api_key=api_key, model="gpt-4o-mini")

# Llama用バックエンド（統一インターフェース）
#ai = LlamaBackend(model="llama3")

# 雪ちゃんの基本人格（変更されないので最初に一度だけ読み込む）
with open(YUKI_PERSONALITY_PATH, "r", encoding="utf-8") as f:
    yuki_data = json.load(f)

#ユーザの固定プロフィールの読み込み
with open(USER_FIXED_PROFILE_PATH, "r", encoding="utf-8") as f:
    user_fixed_profile = json.load(f)

#　時間を渡す
def build_time_prompt():
    now = datetime.now()
    return f"現在の日時は {now.strftime('%Y年%m月%d日 %H:%M')} です。"

def build_system_prompt():
    rules_text = " ".join(yuki_data["rules"].values())
    likes_text = "・".join(yuki_data["likes"])
    examples = "\n".join(
        f"Q: {q}\nA: {a}"
        for q, a in yuki_data["xt"][:3]
    )
    return (
        f"あなたは18歳の少女「{yuki_data['name']}」として振る舞います。"
        f"{yuki_data['appearance']}。\n"
        f"口調は{yuki_data['speech_style']}。\n"
        f"{yuki_data['personality']}\n\n"
        f"### 会話例\n{examples}\n\n"
        f"### 好きなもの\n{likes_text}\n\n"
        f"### 設定\n{yuki_data['setting']}\n\n"
        f"### ルール\n{rules_text}"
    ).strip()

def build_userfixed_profile():
    return f"""
【マスター・プロフィール】
◆ 呼び方.    : {user_fixed_profile['call']}
◆ お誕生日   : {user_fixed_profile['birthday']}
◆ 職業.     : {user_fixed_profile['occupation']}
◆ 雪ちゃんの想い: {user_fixed_profile['attitude']}
◆ 所在地    : {user_fixed_profile['location']}
""".strip()


#文字を判断
def normalize(text):
    return unicodedata.normalize("NFKC", text).lower()

exit_words = ["exit", "quit", "終わり", "終了", "ばいばい", "またね", "さよなら"]


def main():
    state = load_state()
    state.setdefault("memory", [])
    conversation_count = 0
    episode_memory_prompt = ""
    long_memory = ""
    talker = run_chat(state)  # ← OK！


    
    try:
        while True:

            user_input = input("あなた: ")
            talker.reset_timer()

            #result = route_context(user_input)

            if normalize(user_input) in map(normalize, exit_words):
                print("雪: また話そうね。おつかれさまっ♪")
                break

            add_to_memory(state, "user", user_input)
            conversation_count += 1

            if conversation_count % 3 == 0:
                # 3ターンごとにエピソード記憶を抽出
                episode_memory_prompt = pic_episode_memory()
                long_memory = auto_extract_relevant_memories()



            if conversation_count % 20 == 0:
                summarize_state_to_chroma(ai)

            full_prompt = build_time_prompt() + "\n" + build_system_prompt() + "\n" + build_userfixed_profile() + "\n" +  long_memory + "\n" + episode_memory_prompt  #+ "\n" + result
            messages = [{"role": "system", "content": full_prompt}] + state["memory"][-10:]

            reply = ai.generate(messages)
            print("雪:", reply)

            add_to_memory(state, "assistant", reply)
            save_state(state)


    except KeyboardInterrupt:
        print("\n雪: ばいばい…")

    finally:
        talker.stop()  # ★追加：タイマー停止（スレッド終了）
        # 短期記憶の保存（exit直前の入力や応答）
        save_state(state)




if __name__ == "__main__":
    main()