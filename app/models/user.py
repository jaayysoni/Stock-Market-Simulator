# app/models/user.py
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database.db import Base

class User(Base):
    __tablename__ = "user"  # singular to match ForeignKeys in Transaction/Portfolio

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    oauth_provider = Column(String, default=None)
    google_refresh_token = Column(String, nullable=True)
    virtual_balance = Column(Float, default=100000.0)  # virtual money for trading

    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")