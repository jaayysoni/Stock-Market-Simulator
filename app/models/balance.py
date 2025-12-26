# app/models/balance.py
from sqlalchemy import Column, Float, Integer
from app.database.db import Base

class Balance(Base):
    __tablename__ = "balance"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, default=100000.0)  # starting virtual money