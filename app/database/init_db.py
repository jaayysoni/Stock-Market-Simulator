# app/database/init_db.py

from app.database.db import user_engine, UserBase, market_engine, MarketBase

# Import models explicitly
from app.models.user import User           # user_data.db
from app.models.stock import Stock         # market_data.db
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.watchlist import Watchlist

def init_user_db():
    print("📦 Creating tables in user_data.db ...")
    UserBase.metadata.create_all(bind=user_engine)
    print("✅ User DB tables created.")

def init_market_db():
    print("📦 Creating tables in market_data.db ...")
    MarketBase.metadata.create_all(bind=market_engine)
    print("✅ Market DB tables created.")

def init_all():
    init_user_db()
    init_market_db()
    print("🎉 All databases initialized successfully!")

if __name__ == "__main__":
    init_all()

