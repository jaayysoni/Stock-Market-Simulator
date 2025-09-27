# app/services/stock_updater.py
"""
Batch updater for daily close prices.
Uses yfinance for indices (BSE, NSE, Bank Nifty).
Uses Finnhub REST API for other stocks.
"""

import os
import finnhub
import yfinance as yf
from sqlalchemy.orm import Session
from app.database.db import UserSessionLocal
from app.models.stock import Stock

finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))

INDICES = {
    "BSE": "^BSESN",
    "NSE": "^NSEI",
    "BANKNIFTY": "^NSEBANK"
}

def update_eod_prices():
    db: Session = UserSessionLocal()
    stocks = db.query(Stock).all()

    for stock in stocks:
        try:
            if stock.symbol in INDICES:
                # yfinance for indices
                ticker = yf.Ticker(INDICES[stock.symbol])
                data = ticker.history(period="1d", interval="1d")
                if not data.empty:
                    stock.price = float(data["Close"].iloc[-1])
            else:
                # Finnhub REST for other stocks
                candles = finnhub_client.stock_candles(stock.symbol, "D", 1695859200, 1695945600)
                if candles and "c" in candles and len(candles["c"]) > 0:
                    stock.price = candles["c"][-1]
        except Exception as e:
            print(f"⚠️ Error updating {stock.symbol}: {e}")

    db.commit()
    db.close()
    print("✅ End-of-day stock prices updated")