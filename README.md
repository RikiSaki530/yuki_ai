#AIエージェント 「yuki」 の作成記録

##最終目標
・人間のように自然な会話と感情・人格・記憶を持ち、ユーザーと「親友」のような関係を築けるAIを創ること


###技術的な目標
・感情的で論理的な対話ができる
・会話から記憶を作成。人格形成も
・自律的な対話
・音声/視覚/身体(GUI)を持たせる
・AIエージェントとしてさまざまなサポート
・会話のログからファインチューニング等

###AIエージェントとしての目標
・部屋の明かりやクーラーなどの赤外線系を操作できるようにしたい
・LineやXが自律的にできるように
・朝に予定のリマインドや天気の報告等


##中期目標
・音声の実装
・話者認識
・Unitey・Appを使用してGUI化
・視覚実装
・聴覚実装
・自律状態実装


##目標
・yuki側の記憶の実装
・記憶のスコア化の強化
・記憶と感情の結びつけ
・エピソード記憶の実装→記憶
・忘却(これはいらないかも？)


##達成済み
・人格の作成(フォーマット決定済み)
・会話ルールの定義


##使用しているソフト等

cahtGPT
openAI API ←こっちが頭脳
VRoidStudio


# 雪ちゃん MCP統合アクセスシステム

## 概要
本システムは、会話AI「雪ちゃん」が外部リソース（ファイル・API・DB等）にアクセス・操作する機能を、標準プロトコルである MCP（Model Context Protocol）を通じて実現するものです。雪ちゃんが主導して Mastra を経由し、MCPサーバを統一的に操作します。

## システム構成
[ユーザー]
   │
[Live2D UI / AITuberKit]  ← 出力表示・入力受け取り（音声・表情）
   ↑
[雪ちゃんAI Core]
   ├── 記憶管理（state / long_memory）
   ├── 発話ロジック（人格 / スタイル）
   └── → client_mcp.py（MCPリクエスト送信）
             ↓
        [Mastra MCPサーバ]
             ↓
       [MCPスキル / サブサーバ]
             ↓
[外部リソース（API / DB / カレンダー等）]

## 目的と背景
- 各種ツールやデータを共通の形式で扱うことにより、拡張性と保守性を向上
- 雪ちゃんの会話と実行を連動させることで、より自然で実用的な対話エージェントを実現
- MCPを利用することでAIとの接続方式を標準化し、将来的な他ツールとの統合を容易にする

## 機能一覧
| No | 機能名 | 概要 |
|----|--------|------|
| F1 | MCPクライアント実装 | 雪ちゃんからMastraへJSON-RPCで指示を送信 |
| F2 | Mastra起動環境構築 | Mastra MCPサーバをローカルまたはDocker上で常駐実行 |
| F3 | スキル定義 | ファイル/DB/APIなどの操作をMastra側で定義 |
| F4 | 雪ちゃんの判断ロジック | 発話に応じてスキル・パラメータを選出 |
| F5 | 応答整形 | MCPの結果を自然な対話として返答 |
| F6 | 許可スキル管理 | 実行可能なスキルを制限する設定管理機構 |

## 優先スキル（フェーズ1）
| スキルID | スキル名 | 内容 |
|----------|-----------|------|
| S1 | readFile | 日記やToDoなどのローカルファイルを読み取る |
| S2 | getWeather | 天気APIを呼び出して現在地の天候を取得する |
| S3 | getCalendar | Google Calendarから今日の予定を取得する |
| S4 | listTasks | JSONファイル等のローカルタスク一覧を取得する |

## 非機能要件
- 雪ちゃんの発話スタイルや人格を維持しつつ外部情報を統合
- ローカル・クラウド環境での可搬性
- MCPスキルごとの安全制御（権限制限、パス制限など）
- 操作ログの記録

## 今後の展望（フェーズ2以降）
- Notion連携（notion-mcp）
- LINE通知送信（WebhookまたはMCPラッパー）
- データベースへの書き込み系スキル追加
- OCRや画像認識など視覚情報との統合

---

本プロジェクトは段階的に拡張し、雪ちゃんがユーザーの実生活を補助する実用的な「相棒AI」となることを目的としています。