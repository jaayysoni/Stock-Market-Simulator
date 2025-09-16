# app/services/stock_updater.py
import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from app.database.db import UserSessionLocal
from app.models.stock import Stock
import time

BATCH_SIZE = 50  # Number of stocks per batch to fetch safely

def update_stock_prices():
    db: Session = UserSessionLocal()
    stocks = db.query(Stock).all()
    symbols = [stock.symbol for stock in stocks]

    # Fetch in batches
    for i in range(0, len(symbols), BATCH_SIZE):
        batch_symbols = symbols[i:i + BATCH_SIZE]
        try:
            data = yf.download(batch_symbols, period="1d", interval="1m", progress=False)
            # yf.download returns a DataFrame; we get the latest 'Close' price
            if len(batch_symbols) == 1:
                price_data = {batch_symbols[0]: data['Close'][-1]}
            else:
                price_data = data['Close'].iloc[-1].to_dict()

            # Update stock prices in DB
            for stock in stocks[i:i + BATCH_SIZE]:
                if stock.symbol in price_data and not pd.isna(price_data[stock.symbol]):
                    stock.price = float(price_data[stock.symbol])
        except Exception as e:
            print(f"⚠️ Error updating batch {batch_symbols}: {e}")
        time.sleep(1)  # small delay to avoid API rate-limit

    db.commit()
    db.close()
    print("✅ Stock prices updated for all NSE stocks")