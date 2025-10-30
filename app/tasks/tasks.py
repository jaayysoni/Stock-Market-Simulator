# app/tasks/tasks.py

import yfinance as yf
import logging
from datetime import datetime

from app.database.session import SessionLocal  # ✅ unified DB session
from app.models.stock import Stock

# -------------------- Logger Setup --------------------
logger = logging.getLogger("tasks")
logger.setLevel(logging.INFO)


# -------------------- Task: Update Stock Prices --------------------
def update_stock_prices():
    """Fetch current stock prices from Yahoo Finance and update the DB."""
    db = SessionLocal()
    try:
        stocks = db.query(Stock).all()
        if not stocks:
            logger.info("⚠️ No stocks found in database to update.")
            return

        for stock in stocks:
            try:
                ticker = yf.Ticker(stock.symbol)
                data = ticker.history(period="1d")

                if not data.empty:
                    latest_price = data["Close"].iloc[-1]
                    stock.price = float(latest_price)
                    logger.info(f"✅ Updated {stock.symbol} → ₹{stock.price:.2f}")
                else:
                    logger.warning(f"⚠️ No data returned for {stock.symbol}")

            except Exception as e:
                logger.error(f"❌ Error fetching {stock.symbol}: {e}")

        db.commit()
        logger.info("💾 All stock prices updated successfully.")

    except Exception as e:
        logger.error(f"❌ Failed to update stock prices: {e}")
    finally:
        db.close()


# -------------------- Task: Daily Summary --------------------
def daily_summary():
    """Generate daily summary report (placeholder for now)."""
    logger.info(f"📝 Running daily summary task at {datetime.now()}")
    # TODO: Add report generation logic later


# -------------------- Task: Cleanup Expired Sessions --------------------
def cleanup_temp_data():
    """Cleanup expired or temporary guest sessions (placeholder for now)."""
    logger.info(f"🧹 Running cleanup task at {datetime.now()}")
    # TODO: Add cleanup logic later