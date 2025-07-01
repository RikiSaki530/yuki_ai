from datetime import datetime
import requests
import os

from dotenv import load_dotenv
load_dotenv()

def get_weather(city: str = "Naha", country_code: str = "JP") -> dict:
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {
            "type": "error",
            "source": "weather_provider",
            "message": "APIキーが設定されていません。"
        }

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country_code}&units=metric&lang=ja&appid={api_key}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if response.status_code != 200:
            return {
                "type": "error",
                "source": "OpenWeatherMap",
                "message": data.get("message", "天気情報の取得に失敗しました")
            }

        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]

        return {
            "type": "observation.weather",
            "source": "OpenWeatherMap",
            "timestamp": datetime.now().isoformat(),
            "location": {
                "city": city,
                "country": country_code
            },
            "content": {
                "description": weather,
                "temperature": {
                    "current": temp,
                    "min": temp_min,
                    "max": temp_max
                }
            }
        }

    except Exception as e:
        return {
            "type": "error",
            "source": "weather_provider",
            "message": str(e)
        }
    

if __name__ == "__main__":
    print(get_weather())