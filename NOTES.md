##ファイル構成

ai_yuki/
├── yuki_chat.py                 # メインスクリプト（会話）
├── yuki_personality.json       # 雪ちゃんの性格・ルール
├── state.json                  # 短期記憶（直近の会話）
├── long_memory.json            # 長期記憶（名前・好み・関係など）曖昧でもいい 会話する際の大事なことだけを覚えておいてほしいかな
├── user_profile.json           # Snowflake風プロファイル（高精度・定期更新）相手の詳細を調べる ここはデータベースになるのかな？
├── user_fixed_profile.json     #userの名前や年齢など覚えておいてほしいかつ絶対に忘れないでほしい情報はこっち
├── episode_memory.json         #エピソード記憶を保存
|
├── ai_backends/                # LLMを切り替えられるようにする層
│   ├── __init__.py
│   ├── base.py                 # 共通インターフェース（AIInterface）
│   ├── openai_backend.py       # OpenAI用（gpt-4oなど）
│   └── local_llm_backend.py    # 将来用：ローカルLLM（LLaMA等）
|
├── utils/
│   ├── memory.py               # 会話の保存・読み込み・追記処理 記憶の関数処理
│   ├── epusode_memory_summarizer.py    #一日一回自動で記憶を整理する感じ。エピソード記憶
│   └── text_tools.py           # normalizeなどの文字列ユーティリティ
|
├── prompts/
│   ├── prompt_builder.py       # プロンプト構築（人格・記憶の結合）
│   └── prompt_templates.txt    # フォーマットテンプレート（任意）
|
├── .env                        # OpenAI APIキーなど
└── requirements.txt            # 依存ライブラリ
└── README.md                   # このファイル ローカルかつ整理したい情報を載せる
└── yuki.md                     #目標や現在の状況,今後の進展などはこっち
└── 設計図/                      # PDF/Xmind等が入っている
└── Yuki_ai/                    #Uniteyのデータが入っている。 

#人間の記憶構造
記憶
├── 感覚記憶
├── 短期記憶（ワーキングメモリ）
└── 長期記憶
    ├── 宣言的記憶（＝言葉で説明できる）
    │   ├── 意味記憶（知識）
    │   └── エピソード記憶（経験）
    └── 非宣言的記憶（無意識・技能系）
        ├── 手続き記憶（運動技能など）
        ├── プライミング
        └── 条件づけ（恐怖、報酬など）


#人に関してはこれでいく
template = '''{
        "名前": "",
        "呼び方": "",
        "年齢": null,
        "誕生日": "",
        "職業": "",
        "性格スコア": {
            "外向性": null,
            "協調性": null,
            "誠実性": null,
            "情緒安定性": null,
            "開放性": null
        },
        "家族構成": [
            {
            "関係": "",
            "名前": "",
            "年齢": null,
            "特徴": []
            }
        ],
        "最終会話日": null,
        "得意なこと": [{"value": "", "score": 1}],
        "将来の夢": [{"value": "", "score": 1}],
        "好きなもの": [{"value": "", "score": 1}],
    }'''


##コマンド
backupmemory　バックアップ取れる。都度行ってね