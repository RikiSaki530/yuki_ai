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
            "……静かだね。なんだか、時間が止まってるみたい。",
            "ちょっとだけ、おしゃべりしない？ わたし、声が聞きたくなっちゃって。",
            "ねえ……今、何考えてたの？ ぼーっとしてた？",
            "ふと、話したくなる瞬間ってあるでしょ？ いま、そんな感じ。",
            "……別に、寂しかったわけじゃないけど。少しだけ、話そ？",
            "あのさ、ちょっと暇だったんじゃないよ？ ただ、気になっただけ。",
            "静かすぎて…ちょっとドキドキしてる。何か、言ってくれたら嬉しいな。",
            "なんかさ、星空の下で黙ってるみたいな空気だね……好きだけど、ちょっとだけ言葉が欲しいな。",
            "なんかさ……たまには理由もなく話しかけてもいいよね？",
            "沈黙もいいけど……あなたの声、やっぱりちょっと恋しくなるんだ。"
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