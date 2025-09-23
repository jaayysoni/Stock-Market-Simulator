from fastapi import APIRouter, Depends, HTTPException, Request, FastAPI
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.user import User
from app.schemas.user_schema import UserOut
from app.database.session import get_user_db
from app.dependencies.auth import get_current_user
from app.services.auth_service import authenticate_user, create_access_token
from app.services.google_oauth import get_google_auth_url, get_user_info_from_google

router = APIRouter(tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------------
# Manual Registration
# -------------------------------
@router.post("/register")
async def register(request: Request, db: Session = Depends(get_user_db)):
    data = await request.json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        raise HTTPException(status_code=400, detail="All fields required")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(password)
    new_user = User(username=username, email=email, password=hashed_password, oauth_provider="manual")
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": str(new_user.id)})
    response = JSONResponse({"detail": "Signup successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=60*60*24
    )
    return response

# -------------------------------
# Manual Login
# -------------------------------
@router.post("/login")
async def login(request: Request, db: Session = Depends(get_user_db)):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_access_token({"sub": str(user.id)})
    response = JSONResponse({"detail": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=60*60*24
    )
    return response

# -------------------------------
# Current User Info
# -------------------------------
@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# -------------------------------
# Google OAuth Login
# -------------------------------
@router.get("/google-login")
def google_login():
    return RedirectResponse(get_google_auth_url())

# -------------------------------
# Google OAuth Callback
# -------------------------------
@router.get("/google-callback")
async def google_callback(request: Request, db: Session = Depends(get_user_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing Google auth code")

    try:
        user_info = await get_user_info_from_google(code)
        email = user_info.get("email")
        username = user_info.get("name") or (email.split("@")[0] if email else None)

        if not email:
            raise HTTPException(status_code=400, detail="Google account has no email")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(username=username, email=email, password=None, oauth_provider="google")
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token({"sub": str(user.id)})
        response = RedirectResponse(url="/dashboard")  # Use proper GET route
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            samesite="lax",
            max_age=60*60*24
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google OAuth failed: {e}")
    

app = FastAPI()

@app.get("/dashboard")
def dashboard():
    return FileResponse("static/dashboard.html")