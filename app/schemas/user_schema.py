# User input/output models (e.g., LoginRequest, UserOut)
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    virtual_balnce: float

    class Config:
        orm_model = True