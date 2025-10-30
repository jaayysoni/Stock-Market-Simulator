# app/utils/token.py

from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings

# Secret key and algorithm from .env
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours (1 day)

# -------------------------------
# Create access token using user ID
# -------------------------------
def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Generates a JWT token with the user's ID (sub) embedded.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    # Encode JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# -------------------------------
# Verify and decode access token
# -------------------------------
def verify_access_token(token: str, credentials_exception):
    """
    Decodes JWT and returns the user's ID (sub).
    Raises exception if invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # ✅ Now using user_id instead of email
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception