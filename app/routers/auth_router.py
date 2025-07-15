# Handles registration, login, Gmail OAuth, guest sessions
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserCreate, UserOut
from app.models.user import User
from app.database.session import get_db

router = APIRouter(prefix = "/auth", tags = ["Auth"])

@router.post("/register",response_model = UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(user).filter(user.email == user.email).first()
    if db_user:
        raise HTTPException(status_code = 400, detail = "Email already registered")
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user