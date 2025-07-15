# Creates session dependency for route access
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from app.database.db import Base
from contextlib import contextmanager
from sqlalchemy.orm import session
from fastapi import Depends
from app.config import settings
from app.database.db import engine
#create sesionmaker (assumes 'engine' is created in 'db.py')

engine = create_engine(settings.DATABASE_URL, connect_args = {"check_same_thread": False})
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

#Dependency for FastAPI routes
def get_db():
    db:session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#Optional contex manager
@contextmanager
def db_session():
    db: session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
                