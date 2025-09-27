from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import MarketBase  # Use MarketBase for market_data.db

class Transaction(MarketBase):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}  # <-- Fix for "table already defined"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # reference user manually
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    transaction_type = Column(String, nullable=False)  # "buy" or "sell"
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    stock = relationship("Stock", back_populates="transactions")