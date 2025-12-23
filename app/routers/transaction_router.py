# app/routers/trade_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.db import SessionLocal as get_db
from app.models.transaction import Transaction
from app.schemas.transaction_schema import TransactionRead

router = APIRouter(tags=["Transactions"])

# ----------------- Get All Transactions -----------------
@router.get("/", response_model=List[TransactionRead])
def get_all_transactions(db: Session = Depends(get_db)):
    """
    Retrieve all transactions for the universal user (user_id=1).
    Ordered by most recent first.
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == 1)  # universal user
        .order_by(Transaction.timestamp.desc())
        .all()
    )
    return transactions