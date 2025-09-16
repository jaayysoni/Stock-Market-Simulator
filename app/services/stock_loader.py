# app/services/stock_loader.py

import csv
import os
from app.database.db import Base, engine, UserSessionLocal
from app.models.stock import Stock

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Path to Top 500 NSE CSV
CSV_FILE = os.path.join(os.path.dirname(__file__), "../data/top_500_nse.csv")

def load_stocks():
    """Load Top 500 NSE stocks into the database."""
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file not found at {CSV_FILE}")
        return

    db = UserSessionLocal()
    with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        print("CSV Headers:", reader.fieldnames)

        for row in reader:
            symbol = row.get("Symbol")
            name = row.get("Company Name")
            if not symbol or not name:
                continue

            symbol = symbol.strip() + ".NS"

            # Skip if stock already exists in DB
            existing_stock = db.query(Stock).filter_by(symbol=symbol).first()
            if existing_stock:
                continue

            stock = Stock(
                name=name.strip(),
                symbol=symbol,
                exchange="NSE",
                price=0,  # Will be updated later by scheduler
                sector=row.get("Industry", "Unknown").strip()
            )
            db.add(stock)

    db.commit()
    stocks = db.query(Stock).all()
    print("Loaded stocks (first 5):", stocks[:5])
    db.close()
    return stocks

if __name__ == "__main__":
    load_stocks()