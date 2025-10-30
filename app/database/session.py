# app/database/session.py

from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from app.database.db import engine  # ✅ unified engine

# -------------------- Unified Session --------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# -------------------- Dependency for FastAPI --------------------
def get_db():
    """Dependency for all routes using the unified database."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------- Optional Context Manager --------------------
@contextmanager
def db_session():
    """Manual context manager for DB operations outside FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()