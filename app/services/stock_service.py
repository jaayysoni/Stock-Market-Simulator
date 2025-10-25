"""
stock_services.py
-----------------
Handles fetching real-time stock data using Yahoo Finance (yfinance).
Supports single and batch stock queries, plus indices.
"""

import yfinance as yf
from functools import lru_cache
from typing import List, Dict, Optional
import pandas as pd
import os
import time

# ==============================
# Load NSE Top 500
# ==============================
def load_nse_top_500(csv_path: str = "app/data/top_500_nse.csv") -> List[str]:
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return []
    try:
        df = pd.read_csv(csv_path)
        symbols = df["Symbol"].tolist()
        return symbols
    except Exception as e:
        print(f"Error loading NSE top 500 CSV: {e}")
        return []

# ==============================
# Index Symbol Mapping
# ==============================
INDEX_MAPPING = {
    "BSE": "^BSESN",        # BSE Sensex
    "NSE": "^NSEI",         # Nifty 50
    "BANKNIFTY": "^NSEBANK" # Bank Nifty
}

# ==============================
# Format Symbol for yfinance
# ==============================
def format_symbol(symbol: str, exchange: str = "NSE") -> str:
    if symbol in INDEX_MAPPING:
        return INDEX_MAPPING[symbol]
    if exchange.upper() == "NSE":
        return f"{symbol}.NS"
    elif exchange.upper() == "BSE":
        return f"{symbol}.BO"
    else:
        return symbol

# ==============================
# Retry Settings
# ==============================
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# ==============================
# Single Stock Price
# ==============================
@lru_cache(maxsize=500)
def get_stock_price(symbol: str, exchange: str = "NSE") -> float:
    """
    Fetch latest closing price for a single stock or index with retry.
    """
    ticker_symbol = format_symbol(symbol, exchange)
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            ticker = yf.Ticker(ticker_symbol)
            data = ticker.history(period="1d")
            if data.empty:
                raise ValueError(f"No data for {symbol}")
            return round(float(data["Close"][-1]), 2)
        except Exception as e:
            print(f"Attempt {attempt}: Failed to fetch {symbol}: {e}")
            time.sleep(RETRY_DELAY)
    # fallback if all retries fail
    print(f"⚠️ Returning 0 for {symbol} after {MAX_RETRIES} failed attempts")
    return 0.0

# ==============================
# Batch Fetch Stocks
# ==============================
def get_multiple_stock_prices(symbols: List[str], exchange: str = "NSE") -> Dict[str, Dict[str, Optional[float]]]:
    results = {}

    # Separate indices and stocks
    indices = [s for s in symbols if s in INDEX_MAPPING]
    stocks = [s for s in symbols if s not in INDEX_MAPPING]

    # --- Fetch indices individually ---
    for idx in indices:
        price = get_stock_price(idx)
        results[idx] = {"price": price, "change": 0.0}

    # --- Fetch stocks in batch ---
    if stocks:
        formatted_symbols = [format_symbol(s, exchange) for s in stocks]
        data = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                data = yf.download(
                    tickers=" ".join(formatted_symbols),
                    period="1d",
                    interval="1m",
                    group_by="ticker",
                    threads=True,
                    progress=False
                )
                break
            except Exception as e:
                print(f"Attempt {attempt}: Batch fetch failed: {e}")
                time.sleep(RETRY_DELAY)

        if data is None or data.empty:
            print(f"⚠️ Batch fetch failed for all stocks, returning 0 prices")
            for s in stocks:
                results[s] = {"price": 0.0, "change": 0.0}
            return results

        for s, fs in zip(stocks, formatted_symbols):
            try:
                if len(stocks) == 1:
                    close_prices = data["Close"].dropna()
                else:
                    if fs not in data:
                        results[s] = {"price": 0.0, "change": 0.0}
                        continue
                    close_prices = data[fs]["Close"].dropna()

                if close_prices.empty:
                    results[s] = {"price": 0.0, "change": 0.0}
                    continue

                last_price = close_prices.iloc[-1]
                prev_price = close_prices.iloc[-2] if len(close_prices) > 1 else last_price
                change_percent = ((last_price - prev_price) / prev_price) * 100
                results[s] = {
                    "price": round(float(last_price), 2),
                    "change": round(float(change_percent), 2)
                }
            except Exception as e:
                print(f"Error processing {s}: {e}")
                results[s] = {"price": 0.0, "change": 0.0}

    return results

# ==============================
# Top 500 Prices with Cache
# ==============================
CACHE_TTL = 300
_top500_cache = {"data": {}, "timestamp": 0}

def get_top500_prices() -> Dict[str, Dict[str, Optional[float]]]:
    current_time = time.time()
    if current_time - _top500_cache["timestamp"] > CACHE_TTL or not _top500_cache["data"]:
        symbols = load_nse_top_500()
        if not symbols:
            print("⚠️ Top 500 symbols not found, returning empty cache")
            _top500_cache["data"] = {}
            _top500_cache["timestamp"] = current_time
            return _top500_cache["data"]
        symbols += ["BSE", "NSE", "BANKNIFTY"]
        _top500_cache["data"] = get_multiple_stock_prices(symbols)
        _top500_cache["timestamp"] = current_time
    return _top500_cache["data"]

# ==============================
# Test / Debug
# ==============================
if __name__ == "__main__":
    top_500_symbols = load_nse_top_500()
    print(f"Top 500 NSE stocks loaded: {len(top_500_symbols)}")

    # Test single stock
    price = get_stock_price("RELIANCE", "NSE")
    print(f"RELIANCE Price: {price}")

    # Test indices
    indices = get_multiple_stock_prices(["BSE", "NSE", "BANKNIFTY"])
    print("Indices:", indices)

    # Test top 500 batch
    data = get_top500_prices()
    for k, v in list(data.items())[:5]:
        print(k, v)