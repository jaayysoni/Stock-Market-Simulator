# User model with fields like id, email, password, etc.
from sqlalchemy import Column, Integer, String, Float, Boolean
from sqlalchemy.orm import relationship
from app.database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key = True,index = True)
    email = Column(String,unique = True, index = True, nullable = False)
    password = Column(String)
    username = Column(String, index = True,nullable = False)
    virtual_balance = Column(Float, default = 100000.0)
    hashed_password = Column(String,nullable=False)
    is_guest = Column(Boolean, default=False)  # NEW
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete")