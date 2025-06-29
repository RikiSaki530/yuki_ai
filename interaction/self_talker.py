import threading
import time
import random

class SelfTalker:
    def __init__(self, timeout=40):
        self.timeout = timeout
        self.last_input_time = time.time()
        self.triggered = False
        self.running = True

    #話しかけるバリエーション
    def get_message(self):
        topics = [
            "……静かだね。",
            "ちょっとだけ、おしゃべりしない？",
            "そろそろ声かけちゃうよ〜？",
        ]
        return random.choice(topics)

    def start_timer(self):
        def timer_loop():
            while self.running:
                time.sleep(1)
                if not self.triggered and (time.time() - self.last_input_time > self.timeout):
                    print(f"\n雪: {self.get_message()}\nあなた: ", end="", flush=True)
                    self.triggered = True
        threading.Thread(target=timer_loop, daemon=True).start()

    def reset_timer(self):
        self.last_input_time = time.time()
        self.triggered = False

    def stop(self):
        self.running = False