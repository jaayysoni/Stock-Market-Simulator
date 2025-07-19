# app/routers/transaction_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models import User
from app.schemas.transaction_schema import TransactionCreate, TransactionRead
from app.services.transaction_services import buy_stock, sell_stock
from app.dependencies.auth import get_current_user
from app.models.transaction import Transaction

router = APIRouter()


@router.post("/buy", response_model=TransactionRead)
def buy(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        transaction = buy_stock(db, current_user, data)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sell", response_model=TransactionRead)
def sell(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        transaction = sell_stock(db, current_user, data)
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/")
def get_all_transactions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter_by(user_id=current_user.id).order_by(Transaction.timestamp.desc()).all()
    return transactions