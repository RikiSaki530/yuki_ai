import json
import os
from dotenv import load_dotenv
from datetime import datetime

STATE_PATH = os.path.join("talk_memory", "state.json")


STATE_PATH = os.path.join("talk_memory", "state.json")

def load_recent_conversation(n):
    """
    talk_memory/state.json から最新 n 件の会話を取り出す（引数に path を含まない）
    """
    if not os.path.exists(STATE_PATH):
        print(f"⚠️ ファイルが存在しません: {STATE_PATH}")
        return []

    with open(STATE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data[-n:]  # 最新 n 件を取得
    
