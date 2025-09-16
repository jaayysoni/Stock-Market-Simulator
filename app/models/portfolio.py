from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import MarketBase  # use MarketBase for market_data.db

class Portfolio(MarketBase):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # reference user_id manually
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Integer, nullable=False)

    # Relationships
    stock = relationship("Stock", back_populates="portfolios")