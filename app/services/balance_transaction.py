# app/services/balance_transaction.py
from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Session
from app.database.db import Base
from app.models.balance import Balance

class BalanceTransaction(Base):
    __tablename__ = "balance_transaction"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String)  # "ADD", "DEDUCT", "BUY", "SELL"
    amount = Column(Float)
    description = Column(String)       # e.g., "Bought 0.1 BTC"
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


# ----------------------------
# Service function
# ----------------------------
def add_transaction(db: Session, tx_type: str, amount: float, description: str) -> float:
    """
    Adds a balance transaction and updates the universal balance.

    Args:
        db: SQLAlchemy Session
        tx_type: "ADD", "DEDUCT", "BUY", "SELL"
        amount: transaction amount
        description: description text

    Returns:
        Updated balance (float)
    """
    # 1️⃣ Get current balance (universal user)
    balance_obj = db.query(Balance).first()
    if not balance_obj:
        balance_obj = Balance(amount=100000.0)  # initial virtual money
        db.add(balance_obj)
        db.commit()
        db.refresh(balance_obj)

    # 2️⃣ Update balance
    if tx_type in ["BUY", "DEDUCT"]:
        balance_obj.amount -= amount
    elif tx_type in ["SELL", "ADD"]:
        balance_obj.amount += amount
    else:
        raise ValueError(f"Invalid transaction type: {tx_type}")

    db.add(balance_obj)

    # 3️⃣ Record transaction
    tx = BalanceTransaction(
        transaction_type=tx_type,
        amount=amount,
        description=description
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    return round(balance_obj.amount, 2)

