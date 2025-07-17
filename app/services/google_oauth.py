# app/services/google_oauth.py

import httpx
from urllib.parse import urlencode
from app.config import settings

GOOGLE_AUTH_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

def get_google_auth_url():
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    return f"{GOOGLE_AUTH_BASE_URL}?{urlencode(params)}"

async def get_user_info_from_google(code: str):
    # Step 1: Exchange code for access token
    async with httpx.AsyncClient() as client:
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

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        if not access_token:
            raise Exception("Google token exchange failed")

        # Step 2: Use access token to get user info
        userinfo_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        userinfo = userinfo_res.json()

        return {
            "email": userinfo["email"],
            "username": userinfo.get("name", userinfo["email"].split("@")[0])
        }