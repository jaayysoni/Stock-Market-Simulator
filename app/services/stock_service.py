import yfinance as yf
from functools import lru_cache
from typing import List, Dict, Optional

@lru_cache(maxsize=500)
def get_stock_price(symbol: str) -> float:
    """
    Get the latest closing price of a single stock symbol.
    """
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="1d")

    if data.empty:
        raise Exception(f"No data found for symbol: {symbol}")

    return round(data["Close"][-1], 2)


def get_multiple_stock_prices(symbols: List[str]) -> Dict[str, Optional[float]]:
    """
    Get the latest closing prices for multiple stock symbols.
    Returns a dict {symbol: price or None}.
    """
    prices = {}
    for symbol in symbols:
        try:
            prices[symbol] = get_stock_price(symbol)
        except Exception:
            prices[symbol] = None
    return prices