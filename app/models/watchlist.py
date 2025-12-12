# app/models/watchlist.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index, func
from app.database.db import Base


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, ForeignKey("users.email", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        Index("ix_watchlist_email_symbol", "email", "symbol"),
    )