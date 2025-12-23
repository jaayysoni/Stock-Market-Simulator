# app/models/transaction.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.db import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    # FK to crypto table using symbol
    crypto_symbol = Column(String, ForeignKey("cryptos.symbol"), nullable=False, index=True)

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
    timestamp = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    # Relationship to Crypto
    crypto = relationship("Crypto")