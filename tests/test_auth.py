# Tests for login, guest session, Gmail OAuth# app/routers/test_oauth.py
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from app.database.session import get_user_db
from app.services.google_oauth import get_google_auth_url, get_user_info_from_google

router = APIRouter(prefix="/test-oauth", tags=["Test OAuth"])

@router.get("/login")
def test_google_login():
    # Redirect user to Google OAuth page
    return HTMLResponse(f'<a href="/test-oauth/callback">Login with Google</a><br><a href="{get_google_auth_url()}">Click here to login via Google</a>')

@router.get("/callback")
async def test_google_callback(request: Request, db: Session = Depends(get_user_db)):
    code = request.query_params.get("code")
    if not code:
        return HTMLResponse("No code received. Something went wrong.")

    try:
        user_info = await get_user_info_from_google(code)
        return JSONResponse(user_info)  # Just return the user info JSON for testing
    except Exception as e:
        return HTMLResponse(f"OAuth failed: {e}")