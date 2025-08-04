"""Brave Search tool for Braina MCP server."""

from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
import os, requests

# Import the FastMCP instance created in braina.mcp_server
from braina.mcp_server import mcp

load_dotenv()  # Load BRAVE_API_KEY

# ---------- Pydantic models ----------
class BraveIn(BaseModel):
    """Input schema for Brave search."""
    query: str

class BraveOut(BaseModel):
    """Output schema for Brave search."""
    title: str
    snippet: Optional[str] = None
    url: str

# ---------- Tool registration ----------
@mcp.tool(
    name="search_brave",
    description="Brave 検索で上位 1 件を返す"
)
def search_brave(body: BraveIn) -> BraveOut:
    """Call Brave Search API and return the top result."""
    key = os.getenv("BRAVE_API_KEY")
    if not key:
        raise RuntimeError("BRAVE_API_KEY is not set in the environment")

    resp = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"Accept": "application/json", "X-Subscription-Token": key},
        params={"q": body.query, "count": 1},
        timeout=10,
    )
    resp.raise_for_status()
    result = resp.json()["web"]["results"][0]
    return BraveOut(title=result["title"], snippet=result["description"], url=result["url"])