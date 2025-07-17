# db.py - Connects SQLAlchemy to SQLite and initializes engine

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL format
DATABASE_URL = "sqlite:///./stock_market.db"

# Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal class used for creating session objects
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


from sqlalchemy.orm import Session
from fastapi import Depends

# Dependency for getting DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()