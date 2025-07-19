import yfinance as yf
from functools import lru_cache

@lru_cache(maxsize=128)
def get_stock_price(symbol:str):
    ticker = yf.ticker(symbol)
    data = ticker.history(period="1d")

    if data.empty:
        raise Exception(f"No data found for symbol: {symbol}")
    return round(data["Close"][-1],2)
