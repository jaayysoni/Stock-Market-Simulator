from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Request
from fastapi.responses import RedirectResponse
from app.models.user import User
from app.schemas.user_schema import UserCreate
from app.config import settings
from authlib.integrations.starlette_client import OAuth

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT config
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ---------------------
# PASSWORD & AUTH
# ---------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or user.oauth_provider != "manual":
        return None
    if not verify_password(password, user.password):
        return None
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def register_user(db: Session, user_data: UserCreate):
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    
    hashed_pwd = pwd_context.hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_pwd,
        oauth_provider="manual"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ---------------------
# GOOGLE OAUTH SETUP
# ---------------------
oauth = OAuth()
google = oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "openid email profile"}
)

# ---------------------
# GOOGLE OAUTH ROUTES
# ---------------------
async def google_oauth_login(request: Request, db: Session):
    redirect_uri = str(request.url_for("google_callback"))
    return await google.authorize_redirect(request, redirect_uri)

async def google_oauth_callback(request: Request, db: Session):
    token = await google.authorize_access_token(request)
    resp = await google.get("userinfo", token=token)
    user_info = resp.json()

    # Check or create user
    user = db.query(User).filter(User.email == user_info["email"]).first()
    if not user:
        user = User(
            username=user_info.get("name") or user_info["email"].split("@")[0],
            email=user_info["email"],
            password=None,
            oauth_provider="google"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # ✅ JWT now uses email as 'sub' (not id)
    access_token = create_access_token({"sub": user.email})

    # Redirect to dashboard with cookie
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24
    )
    return response