from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

# ✅ updated import
from app.database.db import get_db  
from app.models.user import User
from app.config import settings  # contains SECRET_KEY, ALGORITHM


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    """
    FastAPI dependency to fetch the authenticated user.
    Checks both Authorization header and cookie for JWT.
    ✅ Updated to use email (sub) instead of numeric user_id.
    """
    token: Optional[str] = None

    # 1️⃣ Check for Authorization header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]

    # 2️⃣ If not found, fall back to cookie
    if not token:
        token = request.cookies.get("access_token")

    # 3️⃣ No token found at all
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # 4️⃣ Decode and validate JWT
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_email: Optional[str] = payload.get("sub")  # ✅ now using email
        if not user_email or "@" not in user_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # 5️⃣ Fetch user from DB by email instead of ID
    user: Optional[User] = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user