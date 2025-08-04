from utils.vector_memory import export_all_memories
from utils.memory import summarize_state_to_chroma

import os
from dotenv import load_dotenv

from ai_backends.openai_backend import OpenAIBackend # OpenAI用バックエンド



# OpenAI用バックエンド（統一インターフェース）
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
ai = OpenAIBackend(api_key=api_key, model="gpt-4o-mini")

summarize_state_to_chroma(ai)


# 全メモリを取得
memories = export_all_memories()

if not memories:
    print("メモリが見つかりません。")

# ひとつずつ出力
for idx, m in enumerate(memories, 1):
    print(f"── メモリ {idx} ──")
    print("テキスト :", m["text"])
    print("メタデータ:", m["metadata"])
    print()
