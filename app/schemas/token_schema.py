from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str  # typically "bearer"

class TokenData(BaseModel):
    id: Optional[int] = None  # user ID from token
    email: Optional[str] = None