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
    FastAPI dependency to fetch the currently authenticated user from JWT cookie.
    Raises 401 Unauthorized if the token is missing, invalid, or user does not exist.
    """
    token: Optional[str] = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

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

    user: Optional[User] = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user