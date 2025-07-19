_tools =  [{
    "type": "function",
    "function": {
        "name": "generate_image",
        "description": "Generate a relevant image given a prompt",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The thing to generate. e.g, a lovely spring day",
                },
            },
        },
    },
}] 

def history_process(api_key, message):
    pass

def get_api_key(caller_key, model):
    pass

def add_tools(body):
    toolList = body.get('tools') or []
    toolList += _tools
    return toolList

# Use parts of the stream id
def get_stream_id(body):
    return 0

## auth stuff for later
# AuthX Setup
# Configuration
import jwt
import casbin
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

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
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
@app.get("/u/{public_key}")
def public_profile(public_key: str):
    # Return public info, maybe query DB here later
    return {"user": public_key, "bio": "This is a public profile."}


@app.get("/login/github")
async def github_login():
    """Redirect to GitHub OAuth"""
    # TODO: we can't have localhost:8000 here it has to be
    # inferred from the context of how its being executed
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri=http://localhost:8000/auth/github/callback"
        f"&scope=user:email"
    )
    return RedirectResponse(github_auth_url)

async def github_login_old():
    return await auth.social_login("github")

@app.get("/auth/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    """Handle GitHub OAuth callback"""
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            data={
                "client_id": GITHUB_CLIENT_ID,
                "client_secret": GITHUB_CLIENT_SECRET,
                "code": code,
            },
            headers={"Accept": "application/json"},
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_data = token_response.json()
        github_token = token_data.get("access_token")
        
        if not github_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        # Get user info from GitHub
        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {github_token}"},
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_data = user_response.json()
        
        # Get user email (GitHub might not include email in user endpoint)
        email_response = await client.get(
            "https://api.github.com/user/emails",
            headers={"Authorization": f"token {github_token}"},
        )
        
        emails = email_response.json() if email_response.status_code == 200 else []
        primary_email = next((email["email"] for email in emails if email["primary"]), None)
        
        # Create or update user in database
        github_id = str(user_data["id"])
        username = user_data["login"]
        name = user_data.get("name", username)
        email = primary_email or user_data.get("email")
        
        # TODO: Implement user creation/update logic with your auth_db
        # user = auth_db_module.create_or_update_user(
        #     github_id=github_id,
        #     username=username,
        #     name=name,
        #     email=email
        # )
        
        # Create JWT token
        access_token = create_access_token(
            data={
                "sub": github_id,
                "username": username,
                "name": name,
                "email": email,
            }
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
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

@app.get("/auth/me")
async def get_current_user(current_user: dict = Depends(verify_token)):
    """Get current user info"""
    return current_user

@app.post("/auth/logout")
async def logout():
    """Logout (client should delete token)"""
    return {"message": "Logged out successfully"}

# Protected route example
@app.get("/protected")
async def protected_route(current_user: dict = Depends(verify_token)):
    """Example protected route"""
    return {"message": f"Hello {current_user['username']}!", "user": current_user}

"""
@app.get("/resources/{resource_id}", dependencies=[Depends(auth.get_token_from_request)])
def get_resource(resource_id: str, token: RequestToken = Depends()):
    try:
        user = auth.verify_token(token)
    except Exception:
        raise HTTPException(status_code=403, detail="Invalid or expired token")
    # Casbin middleware enforces policy
    return {"resource": resource_id, "accessed_by": user.sub}

@app.get("/me")
async def me(token: RequestToken = Depends(auth.get_token_from_request)):
    user = auth.verify_token(token)
    return {"sub": user.sub, "scopes": user.payload.get("scopes"), "public_key": user.payload.get("public_key")}
"""

