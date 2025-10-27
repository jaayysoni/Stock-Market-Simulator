# app/routers/transaction_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database.db import get_user_db
from app.models.user import User
from app.models.transaction import Transaction
from app.schemas.transaction_schema import TransactionCreate, TransactionRead
from app.services.transaction_services import buy_stock, sell_stock
from app.dependencies.auth import get_current_user

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

# ----------------- Buy Stock -----------------
@router.post("/buy", response_model=TransactionRead)
def buy(
    data: TransactionCreate,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    try:
        transaction = buy_stock(db, current_user, data)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ----------------- Sell Stock -----------------
@router.post("/sell", response_model=TransactionRead)
def sell(
    data: TransactionCreate,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    try:
        transaction = sell_stock(db, current_user, data)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ----------------- Get All Transactions for Logged-in User -----------------
@router.get("/", response_model=List[TransactionRead])
def get_user_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_user_db)
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_email == current_user.email)
        .order_by(Transaction.timestamp.desc())
        .all()
)
    return transactions
