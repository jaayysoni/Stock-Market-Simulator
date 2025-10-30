# app/database/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings  # ✅ reads from .env if defined

# -------------------------
# Base directory setup
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))        # -> app/database
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR))    # -> Stock-Market-Simulator

# -------------------------
# UNIFIED DATABASE (user_data.db)
# -------------------------
# Try reading from .env first; fallback to local path
DB_PATH = os.path.join(PROJECT_ROOT, "user_data.db")
DB_URL = getattr(settings, "DB_URL", None) or f"sqlite:///{DB_PATH}"

# Create single engine + session
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# -------------------------
# Unified Session Dependency
# -------------------------
def get_db():
    """General dependency for any database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# Aliases for compatibility
# -------------------------
def get_user_db():
    """Alias for unified DB (used in user-related routers)"""
    yield from get_db()


def get_market_db():
    """Alias for unified DB (used in market-related routers)"""
    yield from get_db()