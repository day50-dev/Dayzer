#!/usr/bin/env python
import os
import uvicorn
import casbin
import argparse
import logging
from litellm import completion
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi import Request
from fastapi import Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from authx import AuthX, AuthXConfig, RequestToken
from fastapi_authz import CasbinMiddleware
from sqlalchemy.orm import Session
import auth_db as auth_db

app = FastAPI()

# Initialize DB tables on startup
@app.on_event("startup")
def on_startup():
    auth_db.init_db()

# Dependency to get DB session
def get_db():
    db = auth_db.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# AuthX Setup
"""
auth = AuthX(AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="SUPERSECRETKEY",
    social_providers=["github", "google"],
    JWT_EXPIRATION_DELTA=3600,
))
auth.handle_errors(app)
app.include_router(auth.get_social_router(), prefix="/auth")
"""
# Casbin Setup
enforcer = casbin.Enforcer("casbin_model.conf", "casbin_policy.csv")
app.add_middleware(CasbinMiddleware, enforcer=enforcer)

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

    # Log the chunk between lines 79 and 80
    logger.debug("Chunk between lines 79 and 80: %s", "return StreamingResponse(generate(), media_type='text/event-stream')")
    # Check if OPENROUTER_API_KEY is set
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY is not set. Please set it as an environment variable.")

    uvicorn.run(app, host="0.0.0.0", port=0)

@app.get("/u/{public_key}")
def public_profile(public_key: str):
    # Return public info, maybe query DB here later
    return {"user": public_key, "bio": "This is a public profile."}

@app.get("/resources/{resource_id}", dependencies=[Depends(auth.get_token_from_request)])
def get_resource(resource_id: str, token: RequestToken = Depends()):
    try:
        user = auth.verify_token(token)
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    # Casbin middleware enforces policy
    return {"resource": resource_id, "accessed_by": user.sub}

@app.get("/login/github")
async def github_login():
    return await auth.social_login("github")

@app.get("/auth/github/callback")
async def github_callback(request: Request, db: Session = Depends(get_db)):
    user_data = await auth.social_callback("github", request)

    # Find or create user in DB
    user = db.query(auth_db.User).filter_by(oauth_provider="github", oauth_id=user_data["id"]).first()
    if not user:
        user = auth_db.User(
            username=user_data["login"],
            email=user_data.get("email"),
            oauth_provider="github",
            oauth_id=user_data["id"],
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = auth.create_token(
        subject=str(user.id),
        custom_claims={"scopes": ["read", "write"], "public_key": user.username}
    )
    return RedirectResponse(url=f"/me?token={token}")

@app.get("/me")
async def me(token: RequestToken = Depends(auth.get_token_from_request)):
    user = auth.verify_token(token)
    return {"sub": user.sub, "scopes": user.payload.get("scopes"), "public_key": user.payload.get("public_key")}

