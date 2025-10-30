# app/models/watchlist.py

from sqlalchemy import Column, Integer, String
from app.database.db import Base  # ✅ unified Base

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # store user_id manually
    symbol = Column(String, index=True)