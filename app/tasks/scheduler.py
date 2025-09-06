# app/tasks/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.stock_loader import load_stocks
from app.database.db import SessionLocal
from app.models.stock import Stock
import yfinance as yf
import pandas as pd  # Needed if using pd.isna()

# Create the scheduler
scheduler = BackgroundScheduler()

def update_stock_prices(batch_size=50):
    """Fetch latest prices from Yahoo Finance for all NSE stocks in DB in batches."""
    db = SessionLocal()
    stocks = db.query(Stock).all()
    print(f"Updating prices for {len(stocks)} stocks...")

    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        for stock in batch:
            try:
                ticker = yf.Ticker(stock.symbol)
                info = ticker.info
                price = info.get("regularMarketPrice", stock.price)
                if price is not None and not pd.isna(price):
                    stock.price = float(price)
            except Exception as e:
                print(f"⚠️ Failed to update {stock.symbol}: {e}")
        db.commit()  # Commit per batch to avoid long transactions

    db.close()
    print("✅ Stock prices updated.")

# Schedule jobs
scheduler.add_job(load_stocks, 'interval', hours=24, id="load_nse_stocks")  # Load new stocks once per day
scheduler.add_job(update_stock_prices, 'interval', minutes=10, id="update_stock_prices")  # Update prices every 10 min

def start_scheduler():
    """Start the background scheduler."""
    scheduler.start()
    print("🟢 Scheduler started: load stocks daily, update prices every 10 minutes")