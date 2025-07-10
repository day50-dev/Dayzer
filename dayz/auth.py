from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from authx import AuthX, AuthXConfig, RequestToken
from fastapi_authz import CasbinMiddleware
import casbin

app = FastAPI()

# -------------------------------
# AuthX Setup: OAuth + JWT
# -------------------------------
auth = AuthX(AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="SUPERSECRETKEY",
    social_providers=["github", "google"],
    JWT_EXPIRATION_DELTA=3600,
))
auth.handle_errors(app)
app.include_router(auth.get_social_router(), prefix="/auth")

# -------------------------------
# Casbin Setup: Policy Enforcement
# -------------------------------
enforcer = casbin.Enforcer("casbin_model.conf", "casbin_policy.csv")
app.add_middleware(CasbinMiddleware, enforcer=enforcer)

# -------------------------------
# Public Profile Route
# -------------------------------
@app.get("/u/{public_key}")
def public_profile(public_key: str):
    # This is where you'd query your DB or metadata store
    return {"user": public_key, "bio": "This is a public profile."}

# -------------------------------
# Authenticated Resource Route
# -------------------------------
@app.get("/resources/{resource_id}", dependencies=[Depends(auth.get_token_from_request)])
def get_resource(resource_id: str, token: RequestToken = Depends()):
    try:
        user = auth.verify_token(token)
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid or expired token")

    # Enforced by Casbin middleware; business logic stays clean
    return {"resource": resource_id, "accessed_by": user.sub}

# -------------------------------
# GitHub Login Route
# -------------------------------
@app.get("/login/github")
async def github_login():
    return await auth.social_login("github")

# -------------------------------
# GitHub OAuth Callback Route
# -------------------------------
@app.get("/auth/github/callback")
async def github_callback(request: Request):
    user_data = await auth.social_callback("github", request)
    token = auth.create_token(
        subject=user_data["id"],
        custom_claims={"scopes": ["read", "write"], "public_key": user_data["login"]}
    )
    return RedirectResponse(url=f"/me?token={token}")

# -------------------------------
# Current User Info Route
# -------------------------------
@app.get("/me")
async def me(token: RequestToken = Depends(auth.get_token_from_request)):
    user = auth.verify_token(token)
    return {"sub": user.sub, "scopes": user.payload.get("scopes"), "public_key": user.payload.get("public_key")}

