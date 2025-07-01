from braina.router import route_context

def fetch_context(user_input: str) -> dict:
    result = route_context(user_input)

    if result["type"] == "weather":
        return result
    return None