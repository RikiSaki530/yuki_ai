from pydantic import BaseModel
from braina.mcp_server import mcp  # FastMCP instance shared by the server
import requests


class WeatherIn(BaseModel):
    lat: float
    lon: float


class WeatherOut(BaseModel):
    summary: str
    temperature_c: float


@mcp.tool(
    name="weather_simple",
    description="緯度経度を渡すと現在の簡易天気を返す"
)
def weather_simple(body: WeatherIn) -> WeatherOut:
    url = "https://api.open-meteo.com/v1/forecast"
    r = requests.get(
        url, params={"latitude": body.lat, "longitude": body.lon, "current_weather": "true"}, timeout=10
    )
    r.raise_for_status()
    cw = r.json()["current_weather"]
    return WeatherOut(
        summary=f"風速 {cw['windspeed']} km/h, 天気コード {cw['weathercode']}",
        temperature_c=cw["temperature"],
    )