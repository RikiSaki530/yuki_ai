# yuki_chat_threaded.py
from interaction.self_talker import SelfTalker

def run_chat(state):
    talker = SelfTalker(timeout=40)
    talker.start_timer(state)
    return talker