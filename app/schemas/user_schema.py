from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr = Field(..., example="jaysoni@example.com")
    username: str = Field(..., min_length=3, max_length=20, example="jaysoni")
    password: str = Field(..., min_length=6, example="StrongPass")

class UserOut(BaseModel):
    id: int = Field(..., example=1)
    email: EmailStr = Field(..., example="jaysoni@example.com")
    username: str = Field(..., example="jaysoni")
    virtual_balance: float = Field(..., ge=0, example=100000.0)
    is_guest: bool = Field(..., example=False)

    model_config = {
    "from_attributes": True
}

class UserLogin(BaseModel):
    email: EmailStr = Field(..., example="jaysoni@example.com")
    password: str = Field(..., min_length=8, example="StrongPass123!")