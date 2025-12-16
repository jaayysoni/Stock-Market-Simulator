# app/models/transaction.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    # FK to single user table
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    # FK to crypto table
    crypto_id = Column(Integer, ForeignKey("crypto.id"), nullable=False)

    # Binance symbol (BTCUSDT, ETHUSDT, etc.) for display only
    symbol = Column(String, nullable=False, index=True)

    # BUY / SELL only
    transaction_type = Column(
        String,
        CheckConstraint("transaction_type IN ('BUY','SELL')"),
        nullable=False
    )

    # Decimal crypto quantity
    quantity = Column(Float, nullable=False)

    # Executed price
    price = Column(Float, nullable=False)

    # DB-controlled timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationships
    user = relationship("User", back_populates="transactions")
    crypto = relationship("Crypto", back_populates="transactions")