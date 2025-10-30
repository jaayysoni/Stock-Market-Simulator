# app/auth/oauth.py

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from app.database.session import get_db  # ✅ FIXED
from app.schemas.token_schema import TokenData
from app.services.user_service import get_user_by_email
from app.models.user import User

# ✅ Load environment variables
load_dotenv()

# JWT Configuration from .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# OAuth2 Password Bearer Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)  # ✅ FIXED HERE
) -> User:
    """
    Validates the JWT token and returns the current authenticated user.
    Raises HTTP 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception

    # Fetch user from database
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception

    return user