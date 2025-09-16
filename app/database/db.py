# app/database/db.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# -------------------------
# Base directory
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# -------------------------
# USER DATABASE (user_data.db)
# -------------------------
USER_DB_PATH = os.path.join(BASE_DIR, "user_data.db")
USER_DB_URL = f"sqlite:///{USER_DB_PATH}"

user_engine = create_engine(USER_DB_URL, connect_args={"check_same_thread": False})
UserSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)
UserBase = declarative_base()

def get_user_db():
    db = UserSessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------
# MARKET DATABASE (market_data.db)
# -------------------------
MARKET_DB_PATH = os.path.join(BASE_DIR, "market_data.db")
MARKET_DB_URL = f"sqlite:///{MARKET_DB_PATH}"

market_engine = create_engine(MARKET_DB_URL, connect_args={"check_same_thread": False})
MarketSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=market_engine)
MarketBase = declarative_base()

def get_market_db():
    db = MarketSessionLocal()
    try:
        yield db
    finally:
        db.close()