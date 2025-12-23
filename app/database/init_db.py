# app/database/init_db.py
from app.database.db import Base, engine
from app.models.crypto import Crypto
from app.models.transaction import Transaction

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ Database and tables created successfully!")