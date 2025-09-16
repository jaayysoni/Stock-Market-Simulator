# app/database/session.py
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from fastapi import Depends

from app.database.db import user_engine, market_engine

# -------------------- Session makers --------------------
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)
MarketSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=market_engine)

# -------------------- Dependencies for FastAPI --------------------
def get_user_db():
    """Dependency for routes that use the user database."""
    db = UserSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_market_db():
    """Dependency for routes that use the market database."""
    db = MarketSessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------- Optional context managers --------------------
@contextmanager
def user_db_session():
    db = UserSessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def market_db_session():
    db = MarketSessionLocal()
    try:
        yield db
    finally:
        db.close()