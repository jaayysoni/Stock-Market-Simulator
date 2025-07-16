# app/models/watchlist.py

from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.session import Base

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    symbol = Column(String, index=True)