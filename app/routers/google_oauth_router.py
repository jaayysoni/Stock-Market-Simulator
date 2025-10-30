# app/routers/google_oauth_router.py

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse
import httpx
from urllib.parse import urlencode

from app.config import settings
from app.database.session import get_db  # ✅ unified session import
from app.models.user import User
from app.services.auth_service import create_access_token
from app.services.google_oauth import get_user_info_from_google

router = APIRouter(
    prefix="/auth",
    tags=["Google OAuth"]
)

# Google OAuth URLs
GOOGLE_AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URI = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URI = "https://www.googleapis.com/oauth2/v1/userinfo"

REDIRECT_URI = settings.GOOGLE_REDIRECT_URI
FRONTEND_REDIRECT = "http://localhost:8000/static/dashboard.html"  # ✅ frontend page after login


# -------------------------------
# Step 1: Redirect user to Google
# -------------------------------
@router.get("/google-login")
def google_login():
    """Redirects the user to Google for OAuth2 login."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    auth_url = f"{GOOGLE_AUTH_URI}?{urlencode(params)}"
    return RedirectResponse(auth_url)


# -------------------------------
# Step 2: Handle Google callback
# -------------------------------
@router.get("/google-callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)  # ✅ unified dependency
):
    """Handles callback from Google, verifies the code, and logs in/creates user."""
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing Google auth code")

    # ✅ Fetch user info from Google
    user_info = await get_user_info_from_google(code)
    email = user_info.get("email")
    username = user_info.get("name") or (email.split("@")[0] if email else None)

    if not email:
        raise HTTPException(status_code=400, detail="Google account has no email")

    # ✅ Check if user exists or create new one
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            username=username,
            email=email,
            password=None,
            oauth_provider="google"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # ✅ Generate access token
    access_token = create_access_token({"sub": str(user.id)})

    # ✅ Redirect to dashboard with cookie set
    response = RedirectResponse(url=FRONTEND_REDIRECT)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # set to True when using HTTPS
        samesite="lax",
        max_age=60 * 60 * 24
    )
    return response