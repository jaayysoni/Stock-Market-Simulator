# app/models/crypto.py
from sqlalchemy import Column, Integer, String
from app.database.db import Base

class Crypto(Base):
    __tablename__ = "cryptos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)          # universal symbol, duplicates allowed
    binance_symbol = Column(String, nullable=False) # binance symbol, duplicates allowed