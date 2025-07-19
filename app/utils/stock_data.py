# app/utils/stock_data.py

import yfinance as yf

def get_stock_price(symbol: str) -> float:
    """
    Fetches the latest stock price for a given stock symbol using yfinance.

    Args:
        symbol (str): The stock ticker symbol (e.g., "AAPL", "TSLA")

    Returns:
        float: The latest closing price.

    Raises:
        RuntimeError: If the stock price cannot be fetched.
    """
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")

        if data.empty:
            raise ValueError(f"No price data found for symbol: {symbol}")

        # Return the latest closing price
        return float(data["Close"].iloc[-1])

    except Exception as e:
        raise RuntimeError(f"Error fetching stock price for {symbol}: {e}")