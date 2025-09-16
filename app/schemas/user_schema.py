from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# ---------- Input Schemas ----------

class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="jaysoni@example.com")
    username: str = Field(..., min_length=3, max_length=20, example="jaysoni")
    password: str = Field(..., min_length=6, example="StrongPass")


class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="jaysoni@example.com")
    password: str = Field(..., min_length=8, example="StrongPass123!")


# ---------- Output Schemas ----------

# Minimal user info (no balance) – useful for lightweight responses
class UserBaseOut(BaseModel):
    id: int = Field(..., example=1)
    email: EmailStr = Field(..., example="jaysoni@example.com")
    username: str = Field(..., example="jaysoni")

    model_config = {"from_attributes": True}


# Full user info (includes balance for dashboard/profile)
class UserOut(UserBaseOut):
    virtual_balance: Optional[float] = Field(0.0, ge=0, example=100000.0) 

# Token response (returned on login)
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"