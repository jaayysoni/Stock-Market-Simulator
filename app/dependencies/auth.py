# app/auth/auth.py
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app.database.session import get_user_db
from app.models.user import User
from app.config import settings  # contains SECRET_KEY, ALGORITHM


def get_current_user(request: Request, db: Session = Depends(get_user_db)) -> User:
    """
    FastAPI dependency to fetch the authenticated user.
    Checks both Authorization header and cookie for JWT.
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
        user_id_str: Optional[str] = payload.get("sub")
        if not user_id_str or not user_id_str.isdigit():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        user_id: int = int(user_id_str)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # 5️⃣ Fetch user from DB
    user: Optional[User] = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user