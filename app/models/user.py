# app/models/user.py
from sqlalchemy import Column, Integer, String
from datetime import datetime
from app.database.db import UserBase

class User(UserBase):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # index for every user
    email = Column(String, unique=True, nullable=False)  # email id 
    username = Column(String, unique=True, nullable=False)  # username 
    password = Column(String, nullable=True)  # password 
    oauth_provider = Column(String, default=None)  # "google" for Google OAuth users

    # NEW: Store Google refresh token
    google_refresh_token = Column(String, nullable=True)