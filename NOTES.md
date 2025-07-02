##ファイル構成

ai_yuki/
├── yuki_chat.py                 # メインスクリプト（会話）
├── yuki_chat_threaded.py       # 会話が途切れた際のタイマー管理
|
├── Yuki_memory                 # yukiのメモリー系統
│   └──yuki_personality.json    # 雪ちゃんの性格・ルール
|
├── talk_memory                 # 会話のログ保存用
|   ├──state.json               # 短期記憶（直近の会話）
|   └──long_memory.json         # 長期記憶（名前・好み・関係など）曖昧でもいい 会話する際の大事なことだけを覚えておいてほしいかな
├── user_memory                 #userの情報を管理
│   ├──user_profile.json        # Snowflake風プロファイル（高精度・定期更新）相手の詳細を調べる 
|   |                           #ここはデータベースになるのかな？
│   ├── user_fixed_profile.json #userの名前や年齢など覚えておいてほしいかつ絶対に忘れないでほしい情報はこっち
│   └── episode_memory.json     #エピソード記憶を保存
|
├── ai_backends/                # LLMを切り替えられるようにする層
│   ├── __init__.py
│   ├── base.py                 # 共通インターフェース（AIInterface）
│   ├── openai_backend.py       # OpenAI用（gpt-4oなど）
│   └── llama_backend.py        # llama3 8B(おそらく)
|
├── utils/
│   ├── memory.py               # 会話の保存・読み込み・追記処理 記憶の関数処理 記憶の処理系統に限定する
│   ├── episode_memory_summarizer.py    #一日一回自動で記憶を整理する感じ。エピソード記憶
│   ├── text_tools.py           # normalizeなどの文字列ユーティリティ
│   ├── episode_memory.py       #episode_memoryに現在の会話と関連しているものがないかチェックする関数
|
├── interaction/                #対話インスタラクション
│   └─ self_talker.py           #会話時のタイマーや途切れた際の話題振りなどを関数として管理
|
├── mastra_bridge.py
|
├── braina/                     ←★追加
│   ├── router.py               # 文脈ルーティング（自然文からProviderを選ぶ）
|   ├── intent_classifier.py    # 意図分類ロジック（辞書・LLM・ML対応可）
|   ├── slot_extractor.py       # 場所・日付などのパラメータ抽出
|   ├── mcp_server.py           # MCP対応サーバー（API化 or 外部受付）
│   ├── mcp_server.py           # 外部からの呼び出しを受付けるMCP対応サーバー
│   └── tools                   # 文脈提供者（検索、記憶、天気など）
│       ├── search_tool.py      # Web検索
│       ├── weather_tool.py     # 天気
│       ├── 
│       └── 
|
├── prompts/
│   ├── prompt_builder.py       # プロンプト構築（人格・記憶の結合）
│   └── prompt_templates.txt    # フォーマットテンプレート（任意）
|
├── days_log                    # 毎日の会話を1日ごとに保存
|
├── .env                        # OpenAI APIキーなど
├── requirements.txt            # 依存ライブラリ
├── README.md                   #目標や現在の状況,今後の進展などはこっち
├── NOTES.md                     # このファイル ローカルかつ整理したい情報を載せる
├── 設計図/                      # PDF/Xmind等が入っている
├── noteサムネイル/               #note用のサムネイル
├── Yuki_ai/                    #Uniteyのデータが入っている。 
└──setting/                     # イラストや情報



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