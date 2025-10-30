from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database.db import Base  # ✅ unified Base for user_data.db

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    symbol = Column(String, unique=True, index=True, nullable=False)
    exchange = Column(String, index=True)
    price = Column(Float, nullable=False)
    sector = Column(String)

    portfolios = relationship("Portfolio", back_populates="stock", cascade="all, delete")
    transactions = relationship("Transaction", back_populates="stock", cascade="all, delete")

    def __repr__(self):
        return f"<Stock(name={self.name}, symbol={self.symbol}, price={self.price})>"