from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from authx import AuthX, AuthXConfig, RequestToken
from fastapi_authz import CasbinMiddleware
import casbin
from sqlalchemy.orm import Session
from db import SessionLocal, init_db, User

app = FastAPI()

# Initialize DB tables on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# AuthX Setup
auth = AuthX(AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="SUPERSECRETKEY",
    social_providers=["github", "google"],
    JWT_EXPIRATION_DELTA=3600,
))
auth.handle_errors(app)
app.include_router(auth.get_social_router(), prefix="/auth")

# Casbin Setup
enforcer = casbin.Enforcer("casbin_model.conf", "casbin_policy.csv")
app.add_middleware(CasbinMiddleware, enforcer=enforcer)

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
    user = db.query(User).filter_by(oauth_provider="github", oauth_id=user_data["id"]).first()
    if not user:
        user = User(
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
