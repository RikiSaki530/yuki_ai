from fastapi import FastAPI
import uvicorn
from fastmcp import FastMCP
import braina.tools as tools_pkg
import importlib, pkgutil


mcp = FastMCP("Braina Tools")

# ── tools を登録 ───────────────────────────────
for mod in pkgutil.walk_packages(tools_pkg.__path__, tools_pkg.__name__ + "."):
    importlib.import_module(mod.name)

# --- FastAPI サーバを組み立て ---------------------------------
app = FastAPI(title="Braina MCP Server")

# ★ FastMCP は ASGI アプリなので mount で取り付ける
app.mount("/rpc", mcp)

@app.get("/")
def list_tools():
    # tools_pkg = braina.tools   ← すでに上で import してある
    names = [m.name.split(".")[-1]                      # weather_tool など
             for m in pkgutil.walk_packages(tools_pkg.__path__,
                                            tools_pkg.__name__ + ".")]
    return {"tools": names}