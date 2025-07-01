def route_context(user_input: str) -> str:
    if "天気" in user_input:
        from .providers.weather_provider import get_weather
        return f"天気：{get_weather()}"
    
    elif "調べて" in user_input or "検索" in user_input:
        from .providers.search_provider import search_brave
        return search_brave(user_input)
    
    else:
        return ""  # 何も挿入しない