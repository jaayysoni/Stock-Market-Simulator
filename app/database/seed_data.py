# app/database/seed_data.py

from app.database.db import SessionLocal, Base, engine
from app.models.stock import Stock

def seed():
    print("📦 Ensuring tables exist...")
    Base.metadata.create_all(bind=engine)  # make sure all tables exist

    db = SessionLocal()
    stocks = [
        Stock(name="Apple Inc.", symbol="AAPL", exchange="NASDAQ", price=195.55, sector="Technology"),
        Stock(name="Tesla Inc.", symbol="TSLA", exchange="NASDAQ", price=245.67, sector="Automotive"),
        Stock(name="Amazon.com Inc.", symbol="AMZN", exchange="NASDAQ", price=125.12, sector="E-Commerce"),
    ]
    db.add_all(stocks)
    db.commit()
    db.close()
    print("✅ Seeded sample stock data.")

if __name__ == "__main__":
    seed()