# app/tasks.py

import yfinance as yf
from app.database.db import SessionLocal
from app.models.stock import Stock

def update_stock_prices():
    """Fetch current stock prices from Yahoo Finance and update the DB."""
    db = SessionLocal()
    try:
        stocks = db.query(Stock).all()
        for stock in stocks:
            try:
                ticker = yf.Ticker(stock.symbol)
                data = ticker.history(period="1d")
                if not data.empty:
                    latest_price = data['Close'].iloc[-1]
                    stock.price = float(latest_price)
            except Exception as e:
                print(f"⚠️ Error fetching {stock.symbol}: {e}")
        db.commit()
        print("✅ Stock prices updated")
    finally:
        db.close()

def daily_summary_task():
    """Generate daily summary report (placeholder for now)."""
    print("📝 Running daily summary task")

def cleanup_expired_sessions():
    """Cleanup expired guest sessions (placeholder for now)."""
    print("🧹 Running cleanup task")