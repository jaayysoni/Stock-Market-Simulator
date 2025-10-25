# app/services/google_oauth.py

import httpx
from urllib.parse import urlencode
from typing import Dict, Optional
from app.config import settings

GOOGLE_AUTH_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_google_auth_url(force_consent: bool = False) -> str:
    """
    Returns Google OAuth authorization URL.
    - access_type=offline ensures refresh token is issued.
    - prompt=consent is only sent on first login.
    """
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
    }
    if force_consent:
        params["prompt"] = "consent"  # ensures refresh token is provided first time
    return f"{GOOGLE_AUTH_BASE_URL}?{urlencode(params)}"


async def get_user_info_from_google(code: str) -> Dict[str, Optional[str]]:
    """
    Exchange auth code for access token and fetch user info.
    Returns email, username, and refresh_token (if provided by Google)
    """
    async with httpx.AsyncClient() as client:
        # Step 1: Exchange code for token
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_res.raise_for_status()
        token_data = token_res.json()

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")  # only provided first time

        if not access_token:
            raise Exception("Google token exchange failed")

        # Step 2: Use access token to get user info
        userinfo_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        userinfo_res.raise_for_status()
        userinfo = userinfo_res.json()

        return {
            "email": userinfo.get("email"),
            "username": userinfo.get("name") or (userinfo.get("email", "").split("@")[0] if userinfo.get("email") else None),
            "refresh_token": refresh_token
        }


async def exchange_refresh_token(refresh_token: str) -> Dict[str, str]:
    """
    Use stored refresh token to get a new access token silently.
    """
    if not refresh_token:
        raise Exception("No refresh token provided")

    async with httpx.AsyncClient() as client:
        data = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        resp = await client.post(GOOGLE_TOKEN_URL, data=data)
        resp.raise_for_status()
        token_data = resp.json()

        access_token = token_data.get("access_token")
        if not access_token:
            raise Exception("Failed to refresh Google access token")
        return token_data