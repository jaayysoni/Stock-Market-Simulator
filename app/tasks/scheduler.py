# app/tasks/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.database.session import UserSessionLocal, MarketSessionLocal
from app.models.stock import Stock
import yfinance as yf

# Create the scheduler
scheduler = BackgroundScheduler()

def update_stock_prices(batch_size=50):
    """Fetch latest prices from Yahoo Finance for all stocks in DB in batches."""
    db = UserSessionLocal()
    stocks = db.query(Stock).all()
    print(f"Updating prices for {len(stocks)} stocks...")

    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        for stock in batch:
            try:
                ticker = yf.Ticker(stock.symbol)
                price = ticker.info.get("regularMarketPrice", stock.price)
                if price is not None:
                    stock.price = float(price)
            except Exception as e:
                print(f"⚠️ Failed to update {stock.symbol}: {e}")
        db.commit()  # Commit per batch

    db.close()
    print("✅ Stock prices updated.")

# Schedule jobs (ONLY keep price updater every 10 min)
scheduler.add_job(update_stock_prices, 'interval', minutes=10, id="update_stock_prices")

def start_scheduler():
    """Start the background scheduler."""
    scheduler.start()
    print("🟢 Scheduler started: update prices every 10 minutes")