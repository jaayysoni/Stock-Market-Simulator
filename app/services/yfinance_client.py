# app/services/yfinance_client.py

import yfinance as yf

def get_index_price(symbol: str) -> dict:
    """
    Fetch index price (BSE, NSE, BankNifty) using yfinance.
    Example symbols:
        ^BSESN     -> BSE Sensex
        ^NSEI      -> NSE Nifty 50
        ^NSEBANK   -> Bank Nifty
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")

        if data.empty:
            return {"price": 0, "change": 0}

        # Current price is the last close
        price = float(data["Close"].iloc[-1])

        # Change = Close - Open
        change = float(data["Close"].iloc[-1] - data["Open"].iloc[-1])

        return {"price": price, "change": change}
    except Exception as e:
        print(f"❌ Failed to fetch index {symbol}: {e}")
        return {"price": 0, "change": 0}