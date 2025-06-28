# ai_backends/llama_backend.py

from ollama import chat
from .base import AIInterface  # ← 型を揃えるなら追加推奨

class LlamaBackend(AIInterface):  # ← 継承すると統一できる
    def __init__(self, model="llama3"):
        self.model = model

    def generate(self, messages):
        response = chat(model=self.model, messages=messages)
        return response['message']['content']