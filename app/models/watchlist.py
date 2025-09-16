# app/models/watchlist.py

from sqlalchemy import Column, Integer, String
from app.database.db import MarketBase  # Use MarketBase for market_data.db

class Watchlist(MarketBase):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # store user_id manually
    symbol = Column(String, index=True)