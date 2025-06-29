from interaction.self_talker import SelfTalker

def main():
    talker = SelfTalker(timeout=40)
    talker.start_timer()

    try:
        while True:
            user_input = input("あなた: ").strip()
            talker.reset_timer()

            if user_input.lower() in {"bye", "exit", "終了"}:
                print("雪: また話そうね。おつかれさまっ♪")
                break

            print(f"雪: 『{user_input}』について話そっか。")

    except KeyboardInterrupt:
        print("\n雪: ばいばい…")

    finally:
        talker.stop()

if __name__ == "__main__":
    main()