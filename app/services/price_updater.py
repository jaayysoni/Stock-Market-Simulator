# app/services/price_updater.py
import yfinance as yf
from app.database.session import UserSessionLocal
from app.models.stock import Stock

def update_prices():
    db = UserSessionLocal()
    stocks = db.query(Stock).all()
    print(f"Updating prices for {len(stocks)} stocks...")

    for stock in stocks:
        try:
            ticker = yf.Ticker(stock.symbol)
            stock_info = ticker.info
            stock.price = float(stock_info.get("regularMarketPrice", stock.price))
        except Exception as e:
            print(f"⚠️ Failed to update {stock.symbol}: {e}")
            continue

    db.commit()
    print("✅ Price update completed.")
    db.close()

if __name__ == "__main__":
    update_prices()