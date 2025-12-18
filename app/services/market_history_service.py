# app/services/market_history_service.py

import os
import time
import requests
from dotenv import load_dotenv

from app.utils.cache import set_crypto_history

load_dotenv()

BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")

HEADERS = {"X-MBX-APIKEY": BINANCE_API_KEY} if BINANCE_API_KEY else {}

RATE_LIMIT_WAIT = 120
MAX_LIMIT = 1000


def fetch_daily_history(symbol: str):
    """
    Fetch daily (1d) historical candles from Binance.
    Called once per day per symbol.
    """
    url = f"{BINANCE_BASE_URL}/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": "1d",
        "limit": MAX_LIMIT
    }

    while True:
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)

        if response.status_code in (418, 429):
            print(f"[RATE LIMIT] {symbol} – retrying in {RATE_LIMIT_WAIT}s")
            time.sleep(RATE_LIMIT_WAIT)
            continue

        response.raise_for_status()
        data = response.json()

        if not data:
            raise ValueError(f"No data returned for {symbol}")

        print(f"[OK] Fetched daily history for {symbol}")
        return data


def normalize_daily_history(raw_klines):
    """
    Convert Binance kline array → structured daily candles.
    """
    return [
        {
            "time": k[0],
            "open": float(k[1]),
            "high": float(k[2]),
            "low": float(k[3]),
            "close": float(k[4]),
            "volume": float(k[5])
        }
        for k in raw_klines
    ]


# =========================
# Public orchestration APIs
# =========================

async def load_and_cache_symbol(symbol: str):
    """
    Fetch → normalize → cache daily history for ONE symbol.
    """
    raw = fetch_daily_history(symbol)
    candles = normalize_daily_history(raw)
    await set_crypto_history(symbol, candles)


async def load_and_cache_all_symbols(symbols: list[str]):
    """
    Load & cache history for all symbols (used at startup).
    """
    for symbol in symbols:
        try:
            await load_and_cache_symbol(symbol)
        except Exception as e:
            print(f"[ERROR] Failed loading {symbol}: {e}")