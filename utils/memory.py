import json
import os
from dotenv import load_dotenv
from datetime import datetime

STATE_PATH = "state.json"
ALL_STATE_PATH = "all_state.json"
LONG_MEMORY_PATH = "long_memory.json"
USER_PROFILE_PATH = "user_profile.json"

# ディレクトリ設定
today_str = datetime.now().strftime("%Y-%m-%d")
base_dir = "days_log"
filename = f"episode_{today_str}.json"
DAY_STATE_PATH = os.path.join(base_dir, filename)


load_dotenv()

#読み込み
def load_state():
    if not os.path.exists(STATE_PATH):
        return {"memory": [], "user_name": "", "last_topic": ""}
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


#stateセーブ
def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)




def day_save_state(entry, path=DAY_STATE_PATH):

    # entry は {"role": "user", "content": "..."} の形式を想定
    if not isinstance(entry, dict) or "role" not in entry or "content" not in entry:
        return

    # timestamp を追加（"HH:MM:SS" の形式）
    if "timestamp" not in entry:
        entry["timestamp"] = datetime.now().strftime("%H:%M:%S")

    # 既存データの読み込み（あれば）
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                history = json.load(f)
                if not isinstance(history, list):
                    history = []
        except json.JSONDecodeError:
            history = []
    else:
        history = []

    # 1件追加
    history.append(entry)

    # 保存
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def add_to_memory(state, role, content):
    entry = {"role": role, "content": content}
    state.setdefault("memory", [])
    state["memory"].append(entry)

    if len(state["memory"]) > 20:
        state["memory"] = state["memory"][-20:]

    # ✅ 1件ずつファイルに追記保存
    day_save_state(entry)


#dict型の再起的マージ
def recursive_merge_dict(a, b):
    for key, value in b.items():
        if key in a and isinstance(a[key], dict) and isinstance(value, dict):
            recursive_merge_dict(a[key], value)
        else:
            a[key] = value

# long_memory をマージ
def merge_long_memory(new_data: dict):
    if os.path.exists(LONG_MEMORY_PATH):
        with open(LONG_MEMORY_PATH, "r", encoding="utf-8") as f:
            existing = json.load(f)
    else:
        existing = {}

    for key, value in new_data.items():
        if key in existing:
            # 🧠 スコア付きのリスト（value + score）
            if (
                isinstance(value, list)
                and isinstance(existing[key], list)
                and all(
                    isinstance(i, dict)
                    and isinstance(i.get("value"), str)
                    and isinstance(i.get("score"), int)
                    for i in value
                )
            ):
                merged = {
                    item["value"]: item["score"]
                    for item in existing[key]
                    if isinstance(item, dict)
                    and isinstance(item.get("value"), str)
                    and isinstance(item.get("score"), int)
                }
                for item in value:
                    if not isinstance(item, dict):
                        continue
                    v, s = item.get("value"), item.get("score")
                    if not isinstance(v, str) or not isinstance(s, int):
                        continue
                    if v in merged:
                        merged[v] = max(merged[v], s)
                    else:
                        merged[v] = s
                existing[key] = [{"value": k, "score": v} for k, v in merged.items()]

            # 📚 普通のリスト（所属など）
            elif isinstance(value, list) and isinstance(existing[key], list):
                if all(not isinstance(i, dict) for i in existing[key] + value):
                    # リスト内に dict がなければ重複排除（set）
                    combined = list(dict.fromkeys(existing[key] + value))  # 順序保持
                else:
                    # dict型で "value" を使ってマージ（スコアなし）
                    merged_values = {
                        item["value"]
                        for item in existing[key] + value
                        if isinstance(item, dict) and isinstance(item.get("value"), str)
                    }
                    combined = [{"value": val} for val in merged_values]
                existing[key] = combined

            # 🧩 辞書型（再帰的マージ）
            elif isinstance(value, dict) and isinstance(existing[key], dict):
                recursive_merge_dict(existing[key], value)

            else:
                existing[key] = value  # 型が違うなら新しい方で上書き

        else:
            existing[key] = value  # 初登場のキーはそのまま追加

    with open(LONG_MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)

    print("✅ long_memory.json にマージして更新しました")


# ✅ GPTを使ってリストを意味ベースで整理（類似項目を統合、スコアも引き継ぐ）
def normalize_list_via_gpt_score(item_list, ai, key_name="リスト"):
    import difflib
    import json

    # スコア付きvalueのみ抽出
    raw_values = [
        item["value"]
        for item in item_list
        if isinstance(item, dict) and isinstance(item.get("value"), str)
    ]

    prompt = f"""
次の「{key_name}」のリストは、内容に意味的な重複があります。
似たもの・同じ意味のものをまとめて、簡潔で自然なリストにしてください。
**返答は JSON の list として、value のみ返してください。**
スコアやコメントは不要です。
Markdown の囲い（```）も禁止です。
また、似た意味で統合する場合は、**元の項目と似ている項目のスコアを保てるようにしてください。**

リスト:
{json.dumps(raw_values, ensure_ascii=False)}
"""

    result = ai.generate([
        {"role": "system", "content": "あなたはリストを意味ベースで整理するアシスタントです。"},
        {"role": "user", "content": prompt}
    ]).strip()

    try:
        cleaned_values = json.loads(result)

        if not isinstance(cleaned_values, list):
            print("⚠️ リスト形式ではありません:", result)
            return item_list

        # 元の value→score マップ
        original_scores = {
            item["value"]: item["score"]
            for item in item_list
            if isinstance(item, dict)
            and isinstance(item.get("value"), str)
            and isinstance(item.get("score"), int)
        }

        # 意味的に整理したvalueごとに最も近いscoreを再割当て
        cleaned_scored = []
        for val in cleaned_values:
            if not isinstance(val, str):
                continue
            partial_matches = [k for k in original_scores if val in k or k in val]
            #cutoffを調整して類似度を変更できる
            fuzzy_matches = difflib.get_close_matches(val, original_scores.keys(), n=5, cutoff=0.6)
            candidates = list(set(partial_matches + fuzzy_matches))

            # 類似候補から最大スコアを取得
            matched_scores = [original_scores.get(c) for c in candidates if c in original_scores]
            if not matched_scores:
                matched_scores = [original_scores.get(val, 1)]
            base_score = max(matched_scores)

            # スコア調整ルール・ここを調整すれば記憶の強化とかできる
            if base_score >= 5 and len(candidates) > 1:
                final_score = min(base_score + 1, 10)
            else:
                final_score = base_score

            cleaned_scored.append({"value": val, "score": final_score})
        return cleaned_scored

    except Exception as e:
        print("⚠️ JSON変換失敗:", e)
        print("返答:", result)
        return item_list


# ✅ long_memory.json から user_profile.json を整理・変換して保存する関数
def refine_user_profile(ai):
    import os
    if not os.path.exists(LONG_MEMORY_PATH) or os.path.getsize(LONG_MEMORY_PATH) == 0:
        print("⚠️ long_memory.json が存在しないか空です。user_profile へのコピーをスキップします。")
        return

    try:
        with open(LONG_MEMORY_PATH, "r", encoding="utf-8") as f:
            memory = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ long_memory.json の読み込みに失敗しました（形式エラー）。コピーをスキップします。")
        return

    for key in ["好きなもの", "得意なこと", "将来の夢"]:
        if key in memory and isinstance(memory[key], list):
            original_items = memory[key]
            score_map = {
                item["value"]: item.get("score", 1)
                for item in original_items
                if isinstance(item, dict) and isinstance(item.get("value"), str)
            }

            print(f"\n🧪 {key} の元データ:", original_items)

            cleaned_values = normalize_list_via_gpt_score(original_items, ai, key_name=key)
            print(f"🧪 {key} のGPT整理後:", cleaned_values)

            filtered_items = [
                item for item in cleaned_values
                if isinstance(item, dict) and isinstance(item.get("value"), str)
            ]

            print(f"🧪 {key} のフィルタ後（スコア付き）:", filtered_items)

            if filtered_items:
                memory[key] = filtered_items
            else:
                print(f"⚠️ {key} の filtered_items が空です。元データを維持します。")
                memory[key] = original_items

    # 最終会話日を追加
    memory["最終会話日"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 保存
    with open(USER_PROFILE_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)
        print("✅ user_profile.json に整理・コピーしました")

    with open(LONG_MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=2)
        print("🧹 long_memory.json を初期化しました")


# 会話内容から記憶を抽出して long_memory に保存
def summarize_state_to_long_memory(state, ai):
    history = "\n".join([f"{m['role']}: {m['content']}" for m in state["memory"]])

    template = '''{
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
        "得意なこと": [{"value": "", "score": 1}],
        "将来の夢": [{"value": "", "score": 1}],
        "好きなもの": [{"value": "", "score": 1}],
    }'''
    
    

    prompt = """
以下はAIとユーザーの会話ログです。この情報から「人物プロファイル情報」を抽出してください。

出力形式は、以下のテンプレートにできるだけ従ってください（未使用の項目はnullまたは空欄で構いません）。
**返答は、Markdown の囲い（```json ... ```）を絶対に使わず、JSON本体のみを返してください。説明やコメントも不要です。**
最終会話日は現在の日付を使用してください。フォーマットは YYYY-MM-DD HH:MM です。

テンプレート:
{template}

条件:
- スコアは 1〜10 の整数
- Markdownのコード囲い（```）やコメントは禁止。JSON本体のみ返してください。
-性格スコアは 1~100 の整数で以前の会話から推測してください
会話ログ：
{history}
""".format(template=template, history=history)

    result = ai.generate([
        {"role": "system", "content": "あなたはユーザー情報を抽出するアシスタントです"},
        {"role": "user", "content": prompt}
    ])

    try:
        memory_data = json.loads(result)
        merge_long_memory(memory_data)
        print("✅ long_memory.json に記憶を保存しました")
    except Exception as e:
        print("⚠️ JSON変換に失敗しました:", e)
        print("返答:", result)
