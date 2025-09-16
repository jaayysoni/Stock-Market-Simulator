# app/routers/auth_router.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import random, string

from app.models.user import User
from app.schemas.user_schema import UserOut, TokenResponse
from app.database.session import get_user_db
from app.dependencies.auth import get_current_user
from app.services.auth_service import authenticate_user, create_access_token
from app.services.google_oauth import get_google_auth_url, get_user_info_from_google

router = APIRouter(tags=["Auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# -------------------------------
# ✅ Register a new user 
# -------------------------------
@router.post("/register", response_model=UserOut)
async def register(request: Request, db: Session = Depends(get_user_db)):
    try:
        data = await request.json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            raise HTTPException(status_code=400, detail="All fields are required")

        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        password = pwd_context.hash(password)
        new_user = User(
            username=username,
            email=email,
            password=password,
            # is_guest=False
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}")


# -------------------------------
# ✅ Email/password Login (JSON)
# -------------------------------
@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: Session = Depends(get_user_db)):
    try:
        data = await request.json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password required")

        user = authenticate_user(db, email, password)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        access_token = create_access_token(data={"sub": str(user.id)})

        # ✅ Only return token, leave balance for /auth/me
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {e}")
# -------------------------------
# ✅ Guest Login
# -------------------------------
# @router.post("/guest-login")
# def guest_login(db: Session = Depends(get_user_db)):
#     try:
#         random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
#         guest_username = f"guest_{random_id}"
#         guest_email = f"{guest_username}@guest.local"

#         user = db.query(User).filter(User.email == guest_email).first()
#         if not user:
#             user = User(
#                 username=guest_username,
#                 email=guest_email,
#                 password="",
#                 is_guest=True
#             )
#             db.add(user)
#             db.commit()
#             db.refresh(user)

#         access_token = create_access_token(data={"sub": str(user.id)})
#         return {
#             "access_token": access_token,
#             "token_type": "bearer",
#             "user": {
#                 "id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "virtual_balance": user.virtual_balance,
#                 "is_guest": user.is_guest
#             }
#         }

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Guest login failed: {e}")


# -------------------------------
# ✅ Current User
# -------------------------------
@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


# -------------------------------
# ✅ Google Login
# -------------------------------
@router.get("/google-login")
def google_login():
    return RedirectResponse(get_google_auth_url())


# -------------------------------
# ✅ Google Callback
# -------------------------------
@router.get("/google-callback")
async def google_callback(request: Request, db: Session = Depends(get_user_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing Google auth code")

    try:
        user_info = await get_user_info_from_google(code)
        email = user_info.get("email")
        username = user_info.get("name") or email.split("@")[0]

        if not email:
            raise HTTPException(status_code=400, detail="Google account has no email")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                username=username,
                email=email,
                password="",
                # is_guest=False
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        access_token = create_access_token(data={"sub": str(user.id)})

        return JSONResponse({
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "virtual_balance": user.virtual_balance,
                # "is_guest": user.is_guest
            }
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google OAuth failed: {e}")