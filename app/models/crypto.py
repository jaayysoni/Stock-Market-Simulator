# app/models/crypto.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database.db import Base

class Crypto(Base):
    __tablename__ = "crypto"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    universal_symbol = Column(String, unique=True, nullable=False)
    binance_symbol = Column(String, unique=True, nullable=False)

    # Relationships
    portfolios = relationship("Portfolio", back_populates="crypto", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="crypto", cascade="all, delete-orphan")