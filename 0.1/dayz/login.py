# app.py
from fastapi import FastAPI, Depends
from authx import AuthX, AuthXConfig, RequestToken
from fastapi_authz import CasbinMiddleware
import casbin

# AuthX setup
auth = AuthX(AuthXConfig(
    JWT_ALGORITHM="HS256",
    JWT_SECRET_KEY="YOUR_SECRET",
    social_providers=["github", "google"],
))
auth.handle_errors(app)
app.include_router(auth.get_social_router(), prefix="/auth")

# Casbin setup
enforcer = casbin.Enforcer("casbin_model.conf", "casbin_policy.csv")
app.add_middleware(CasbinMiddleware, enforcer=enforcer)

@app.get("/u/{public_key}")
def public_profile(public_key: str):
    # lookup user metadata by public_key
    return { "bio": "Profile info here" }

@app.get("/resources/{id}", dependencies=[Depends(auth.get_token_from_request)])
def get_resource(id: str, token: RequestToken = Depends()):
    user = auth.verify_token(token)
    return business_logic.get(id, user.sub)

