from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base  # ✅ unified Base for user_data.db

# ================= Portfolio Model =================
class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # reference user_id manually
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Float, nullable=False)  # allow fractional shares if needed

    # Relationships
    stock = relationship("Stock", back_populates="portfolios")
    transactions = relationship("PortfolioTransaction", back_populates="portfolio", cascade="all, delete-orphan")


# ================= Portfolio Transaction Model =================
class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transactions"  # changed table name to avoid clash

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    type = Column(String, nullable=False)  # "buy" or "sell"
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationship
    portfolio = relationship("Portfolio", back_populates="transactions")