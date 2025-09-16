# app/routers/portfolio_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.auth import get_current_user
from app.database.session import get_user_db
from app.models.user import User

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

@router.get("/")
async def get_portfolio_summary(
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "message": f"Welcome {current_user.username}, this is your portfolio summary."
    }

@router.get("/holdings")
async def get_portfolio_holdings(
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    return {
        "message": f"User {current_user.username}, here are your stock holdings."
    }