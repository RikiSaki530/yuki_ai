# ai_backends/base.py

from abc import ABC, abstractmethod

class AIInterface(ABC):
    @abstractmethod
    def generate(self, messages: list[dict]) -> str:
        pass
