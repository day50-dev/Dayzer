#!/usr/bin/env python
import os
import uvicorn
import argparse
import logging
import httpx
from datetime import datetime, timedelta
from litellm import completion
from fastapi import FastAPI, Depends, Request, HTTPException, status
from fastapi.responses import JSONResponse, StreamingResponse, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_authz import CasbinMiddleware
from sqlalchemy.orm import Session
from authx import AuthX, AuthXConfig, RequestToken
import auth_db as auth_db
from contextlib import asynccontextmanager
import toolcalls


# Initialize DB tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # before load
    auth_db.init_db()
    yield
    # after

app = FastAPI(lifespan=lifespan)

# Dependency to get DB session
def get_db():
    db = auth_db.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def completion_caller(request, body):
    api_key = request.headers.get("API_KEY") # get it from the header
    model = body['model']

    body['messages'] = Dayzer.history_process(api_key, body['messages'])
    user_api_key = Dayzer.get_api_key(caller_key=api_key, model=model)
    tools = Dayzer.add_tools(body)

    response = completion(
        base_url="http://localhost:8080/",
        api_key=user_api_key,
        model=model,
        messages=body["messages"],
        tools=tools,
        stream=body.get('stream') or False
    )
    return response

@app.post("/v1/chat/completions")
async def chat_completions_proxy(request: Request):
    body = await request.json()
    api_key = os.environ.get("OPENROUTER_API_KEY")

    try:
        response = completion_caller(request, body)

        if not stream:
            return JSONResponse(response.json())
        
        def generate():
            for chunk in response: 
                yield f"data:{chunk.model_dump_json()}\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        return JSONResponse(
            {"error": f"OpenAI API error: {str(e)}"},
            status_code=500
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logger = logging.getLogger(__name__)

    # Check if OPENROUTER_API_KEY is set
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY is not set. Please set it as an environment variable.")

    uvicorn.run(app, host="0.0.0.0", port=8778)


