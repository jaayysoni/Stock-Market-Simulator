# app/routers/google_oauth_router.py

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
import httpx
from app.config import settings
from app.database.session import get_user_db
from app.models.user import User
from app.services.auth_service import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Google OAuth"]
)

GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URI = "https://www.googleapis.com/oauth2/v1/userinfo"

REDIRECT_URI = "http://localhost:8000/auth/google-callback"  # Update if deployed

@router.get("/google-login")
def google_login():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }

    from urllib.parse import urlencode
    return RedirectResponse(url=f"{GOOGLE_AUTH_URI}?{urlencode(params)}")

@router.get("/google-callback")
async def google_callback(request: Request, db: Session = Depends(get_user_db)):
    code = request.query_params.get("code")

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not found.")

    # Exchange code for access token
    token_data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URI, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()

        access_token = token_json["access_token"]

        # Get user info from Google
        userinfo_response = await client.get(
            GOOGLE_USERINFO_URI,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo_response.raise_for_status()
        userinfo = userinfo_response.json()

    email = userinfo["email"]
    username = userinfo.get("name") or email.split("@")[0]

    # Check if user exists, otherwise create one
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            username=username,
            password="",  # No password for Google users
            # is_guest=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # Generate access token
    jwt_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": jwt_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "virtual_balance": user.virtual_balance,
            # "is_guest": user.is_guest
        }
    }