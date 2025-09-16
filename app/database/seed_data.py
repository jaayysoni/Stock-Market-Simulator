# app/database/seed_data.py

from app.database.db import MarketSessionLocal, MarketBase, market_engine
from app.models.stock import Stock

def seed():
    print("📦 Ensuring market tables exist...")
    MarketBase.metadata.create_all(bind=market_engine)  # create only market tables

    db = MarketSessionLocal()

    # Check if stocks already exist
    if db.query(Stock).first():
        print("⚡ Market data already seeded. Skipping.")
        db.close()
        return

    stocks = [
        Stock(name="Reliance Industries", symbol="RELIANCE", exchange="NSE", price=2450.00, sector="Conglomerate"),
        Stock(name="Tata Consultancy Services", symbol="TCS", exchange="NSE", price=3450.00, sector="IT Services"),
        Stock(name="Infosys", symbol="INFY", exchange="NSE", price=1550.00, sector="IT Services"),
        Stock(name="HDFC Bank", symbol="HDFCBANK", exchange="NSE", price=1650.00, sector="Banking"),
        Stock(name="ICICI Bank", symbol="ICICIBANK", exchange="NSE", price=980.00, sector="Banking"),
        Stock(name="State Bank of India", symbol="SBIN", exchange="NSE", price=590.00, sector="Banking"),
    ]

    db.add_all(stocks)
    db.commit()
    db.close()
    print("✅ Seeded Indian stock market data.")

if __name__ == "__main__":
    seed()