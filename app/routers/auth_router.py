from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import random, string

from app.models.user import User
from app.schemas.user_schema import UserCreate, UserOut
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.services.auth_service import authenticate_user, create_access_token
from app.services.google_oauth import get_google_auth_url, get_user_info_from_google
from app.config import settings

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ✅ Register a new user
@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_guest=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ✅ Email/password Login
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "virtual_balance": user.virtual_balance,
            "is_guest": user.is_guest
        }
    }

# ✅ Guest Login
@router.post("/guest-login")
def guest_login(db: Session = Depends(get_db)):
    random_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    guest_username = f"guest_{random_id}"
    guest_email = f"{guest_username}@guest.local"

    existing_guest = db.query(User).filter(User.email == guest_email).first()
    if existing_guest:
        user = existing_guest
    else:
        user = User(
            username=guest_username,
            email=guest_email,
            hashed_password="",
            is_guest=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "virtual_balance": user.virtual_balance,
            "is_guest": user.is_guest
        }
    }

# ✅ Get current logged-in user info
@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# ✅ Google Login - Redirect to Google
@router.get("/google-login")
def google_login():
    return RedirectResponse(get_google_auth_url())

# ✅ Google Callback - Get token and create user
@router.get("/google-callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    if not code:
        raise HTTPException(status_code=400, detail="Missing Google auth code")

    try:
        user_info = await get_user_info_from_google(code)
        email = user_info["email"]
        username = user_info["username"]

        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                username=username,
                email=email,
                hashed_password="",
                is_guest=False
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
                "is_guest": user.is_guest
            }
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))