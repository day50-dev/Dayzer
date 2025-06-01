# main.py
import os
import json
import asyncio
from typing import AsyncIterator

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx

app = FastAPI()

# Dummy key store
KEY_STORE = {
    "sk-team-abc123": {"user": "alice", "team": "red"},
    "sk-team-def456": {"user": "bob", "team": "blue"},
}

# Stub for shared context
async def load_shared_context(user_id: str, team_id: str) -> list:
    # Replace this with your shared memory logic
    return [{"role": "system", "content": f"User {user_id} from team {team_id} is requesting help."}]

async def stream_response(resp: httpx.Response) -> AsyncIterator[bytes]:
    async for chunk in resp.aiter_raw():
        yield chunk

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    key = auth_header.split(" ", 1)[1].strip()
    user_data = KEY_STORE.get(key)
    if not user_data:
        raise HTTPException(status_code=403, detail="Invalid API key")

    body = await request.json()
    model = body.get("model")
    messages = body.get("messages", [])

    if not model:
        raise HTTPException(status_code=400, detail="Model is required")

    # Inject shared context
    context = await load_shared_context(user_data["user"], user_data["team"])
    full_messages = context + messages
    body["messages"] = full_messages

    # Route to OpenRouter
    upstream_url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY', '')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://yourdomain.com/",
        "X-Title": "TeamCollabProxy"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        upstream_resp = await client.post(
            upstream_url,
            headers=headers,
            json=body,
            stream=True
        )

        return StreamingResponse(
            stream_response(upstream_resp),
            status_code=upstream_resp.status_code,
            headers={"Content-Type": "text/event-stream"}
        )

