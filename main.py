import os
import uvicorn
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
OPENROUTER_URL = "https://openrouter.ai/api/v1"
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")  # MCP server base URL

if not SUPABASE_API_KEY or not SUPABASE_PROJECT_URL:
    raise RuntimeError("Missing Supabase environment configuration.")

app = FastAPI()

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


# --- API Routes ---

@app.api_route("/mcp/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def handle_mcp(path: str, request: Request, authorization: str = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    # TODO: Verify API key against Supabase or DB here
    return await mcp_proxy(request, path)


@app.api_route("/{provider:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def handle_request(provider: str, request: Request, authorization: str = Header(default=None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    # TODO: Verify API key against Supabase or DB here
    target_url = f"{OPENROUTER_URL}/{provider}"
    return await proxy_request(request, target_url)


if __name__ == "__main__":
    uvicorn.run("llm_proxy_server:app", host="0.0.0.0", port=4000, reload=True)

