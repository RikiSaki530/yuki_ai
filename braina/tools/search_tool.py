import requests
import os

from dotenv import load_dotenv
load_dotenv()

def search_brave(query: str) -> str:

    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {
        "q": query,
        "count": 3  # 最上位1件だけ
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        top_result = data["web"]["results"][0]
        title = top_result["title"]
        snippet = top_result["description"]
        link = top_result["url"]
        return f"{title}\n{snippet}\n詳しくはこちら：{link}"
    else:
        return "ごめん、Brave検索中に問題が発生したみたい。"
    
if __name__ == "__main__":
    print(search_brave("ChatGPTの最新情報"))