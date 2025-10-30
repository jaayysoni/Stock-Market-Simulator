# app/models/user.py
from sqlalchemy import Column, Integer, String
from app.database.db import Base  # ✅ unified Base (replaces UserBase)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    oauth_provider = Column(String, default=None)
    google_refresh_token = Column(String, nullable=True)