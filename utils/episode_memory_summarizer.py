import json
import os
from dotenv import load_dotenv
from datetime import datetime

# ディレクトリ設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # このファイルのある場所
LOG_DIR = os.path.join(BASE_DIR, "../days_log")
EPISODE_MEMORY_PATH = os.path.join(BASE_DIR, "../episode_memory.json")


today_str = datetime.now().strftime("%Y-%m-%d")
base_dir = "days_log"
filename = f"episode_{today_str}.json"
DAY_STATE_PATH = os.path.join(base_dir, filename)

#　時間を渡す
def build_time_prompt():
    now = datetime.now()
    return f"現在の日時は {now.strftime('%Y年%m月%d日')} です。"


# 日ごとの状態を保存する関数
def create_daily_json_file(base_dir="days_log"):
    # 今日の日付を取得（例：2025-06-25）
    today_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"episode_{today_str}.json"
    filepath = os.path.join(base_dir, filename)

    # ディレクトリがなければ作成
    os.makedirs(base_dir, exist_ok=True)

    # ファイルがなければ空のリストで新規作成
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"✅ 新しいファイルを作成しました: {filepath}")
    else:
        print(f"📁 既にファイルがあります: {filepath}")

    return filepath  # ファイルパスを返す（保存・追記用に）



# 会話内容からエピソードを抽出して episode_memory に保存
def summarize_state_to_episode_memory( ai):

    # JSONファイルから履歴を読み込む
    if os.path.exists(DAY_STATE_PATH):
        with open(DAY_STATE_PATH, "r", encoding="utf-8") as f:
            memory_list = json.load(f)
    else:
        memory_list = []


    # 会話履歴の文字列生成（role: content 形式）
    history = "\n".join([f"{m['role']}: {m['content']}" for m in memory_list])

    template = '''{
    "日付": "",
    "話題": "",
    "関係者": [""],
    "場所・状況": "",
    "会話要約": "",
    "感情": {
        "ユーザー": "",
        "雪ちゃん": ""
    },
    "記憶の種類": "",
    "タグ": [],
    "スコア": null
    }'''

    sample = '''{
  "日付": "2025-06-25",
  "話題": "星の話",
  "関係者": ["雪ちゃん"],
  "場所・状況": "夜、公園でおしゃべりしていた",
  "会話要約": "星の話をして、ユーザーが星空が好きだと判明した。",
  "感情": {
    "ユーザー": "嬉しい",
    "雪ちゃん": "嬉しい"
  },
  "記憶の種類": "好み・癒しに関する記憶（永続）",
  "タグ": ["星", "癒し", "好み", "感情共有"],
  "スコア": 3
}'''
    

    prompt = """
以下は1日のAIとユーザーの会話ログです。この情報から「エピソード記憶」を抽出してください。

テンプレート:
{template}

サンプル:
{sample}

条件:
- スコアは 1〜10 の整数です。重要度でスコアづけしてください。
- Markdownのコード囲い（```）やコメントは禁止。JSON本体のみ返してください。
- 日付は現在の日付を使用してください。フォーマットは YYYY-MM-DD HH:MM です。
- 会話内容から、意味のあるエピソードがあれば最大3件まで抽出してください（なければ1件でも構いません）。
- 情報が不明な場合は空欄（""）または null にしてください。推測で埋めないでください。
- 「タグ」は最大4つまで、短く具体的な単語で記述してください。
-「記憶の種類」は好み・癒し・苦手・夢など、内容に応じた意味的なカテゴリを自由に記述してください（最大3つまで）。
- 会話のログがなければ、空のテンプレートを返してください。

会話ログ：
{history}
""".format(template=template , sample=sample ,  history=history)
    
    all_prompt = prompt + "\n\n" + build_time_prompt()

    result = ai.generate([
        {"role": "system", "content": "あなたはユーザー情報を抽出するアシスタントです"},
        {"role": "user", "content": all_prompt}
    ])

    try:
        memory_data = json.loads(result)  # 生成された記憶のデータ（辞書型など）

        # 既存の記憶を読み込み（なければ空リスト）
        if os.path.exists(EPISODE_MEMORY_PATH):
            with open(EPISODE_MEMORY_PATH, "r", encoding="utf-8") as f:
                try:
                    existing = json.load(f)
                    if not isinstance(existing, list):
                        existing = []
                except json.JSONDecodeError:
                    existing = []
        else:
            existing = []

        # 新しいデータを追加
        existing.append(memory_data)

        # 上書き保存（全エピソード含むリストとして）
        with open(EPISODE_MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

        print("✅ episode_memory.json に記憶を追加しました")

    except Exception as e:
        print("⚠️ JSON変換または保存に失敗しました:", e)
        print("返答:", result)

if __name__ == "__main__":
    import sys
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))

    from yuki_chat import ai  # 必要に応じて変更
    
    summarize_state_to_episode_memory(ai)
    #create_daily_json_file()  # 日ごとの状態を保存する関数を呼び出し