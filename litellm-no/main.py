import os
import uvicorn
from fastapi import FastAPI, Request, Header, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from dotenv import load_dotenv
import json
import uuid
from pathlib import Path
from typing import Optional

load_dotenv()

SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
OPENROUTER_URL = "https://openrouter.ai/api/v1"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")  # MCP server base URL

if not SUPABASE_API_KEY or not SUPABASE_PROJECT_URL:
    raise RuntimeError("Missing Supabase environment configuration.")

app = FastAPI()

HISTORY_DIR = Path("conversation_history")
HISTORY_DIR.mkdir(exist_ok=True)

# Utility for history JSON files per user

def user_history_path(user_id: str) -> Path:
    return HISTORY_DIR / f"{user_id}.json"

def load_user_history(user_id: str) -> dict:
    path = user_history_path(user_id)
    if not path.exists():
        return {"threads": []}
    with open(path, "r") as f:
        return json.load(f)

def save_user_history(user_id: str, data: dict):
    with open(user_history_path(user_id), "w") as f:
        json.dump(data, f, indent=2)


# --- Core Proxy to OpenRouter ---

async def proxy_request(request: Request, target_url: str):
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    body = await request.body()
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            resp = await client.request(
                method,
                target_url,
                headers=headers,
                content=body,
                stream=True,
            )
            return StreamingResponse(resp.aiter_raw(), status_code=resp.status_code, headers=dict(resp.headers))
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))


# --- Stub MCP Client Integration ---

async def mcp_proxy(request: Request, path: str):
    """
    Proxy MCP-related requests to the MCP server.
    This can be expanded to implement richer MCP client features,
    e.g. caching, validation, OAuth, or context manipulation.
    """
    if not MCP_SERVER_URL:
        raise HTTPException(status_code=500, detail="MCP_SERVER_URL not configured.")

    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)
    body = await request.body()
    target_url = f"{MCP_SERVER_URL}/{path}"

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            resp = await client.request(
                method,
                target_url,
                headers=headers,
                content=body,
                stream=True,
            )
            # For demo, if JSON response, parse & modify here if needed
            if 'application/json' in resp.headers.get('content-type', ''):
                json_data = resp.json()
                # Add any MCP-layer processing here, e.g. validation, augmentation
                return JSONResponse(content=json_data, status_code=resp.status_code)
            else:
                return StreamingResponse(resp.aiter_raw(), status_code=resp.status_code, headers=dict(resp.headers))
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=str(e))


# --- API Key Validation Stub ---
# TODO: Implement proper Supabase-based API key validation and user extraction

def validate_api_key(api_key: str) -> Optional[str]:
    """
    Validate API key and return user_id or None if invalid.
    For now, accepts any non-empty key and returns a fixed demo user.
    """
    if not api_key:
        return None
    # TODO: query Supabase to validate API key and fetch user ID
    return "demo_user"


# --- History Service Endpoints ---

@app.get("/history/threads")
async def list_threads(
    authorization: str = Header(...),
    topic: Optional[str] = Query(None),
):
    user_id = validate_api_key(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid API key")

    history = load_user_history(user_id)
    threads = history.get("threads", [])

    if topic:
        threads = [t for t in threads if topic.lower() in t.get("topic", "").lower()]

    summary = [{"id": t["id"], "topic": t["topic"], "last_updated": t.get("last_updated")} for t in threads]
    return {"threads": summary}

@app.post("/history/threads")
async def add_thread(
    thread_data: dict,
    authorization: str = Header(...),
):
    user_id = validate_api_key(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid API key")

    history = load_user_history(user_id)
    thread_id = str(uuid.uuid4())
    thread_data["id"] = thread_id
    history.setdefault("threads", []).append(thread_data)
    save_user_history(user_id, history)
    return {"id": thread_id, "message": "Thread added"}


# --- MCP Route ---

@app.api_route("/mcp/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def handle_mcp(path: str, request: Request, authorization: str = Header(...)):
    user_id = validate_api_key(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid API key")
    # TODO: Verify API key against Supabase or DB here
    return await mcp_proxy(request, path)


# --- OpenRouter Proxy Route ---

@app.api_route("/{provider:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def handle_request(provider: str, request: Request, authorization: str = Header(...)):
    user_id = validate_api_key(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid API key")
    # TODO: Verify API key against Supabase or DB here

    target_url = f"{OPENROUTER_URL}/{provider}"
    return await proxy_request(request, target_url)


if __name__ == "__main__":
    uvicorn.run("llm_proxy_server:app", host="0.0.0.0", port=4000, reload=True)

