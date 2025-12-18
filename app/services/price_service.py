# app/services/price_service.py
import json
from typing import List, Optional
from datetime import datetime, timedelta
import random

from app.database.db import SessionLocal
from app.models.crypto import Crypto
from app.utils.redis_client import get_redis
from app.utils.cache import get_crypto_history as cache_get_history, set_crypto_history as cache_set_history

# ==============================
# Live crypto prices
# ==============================
async def get_all_crypto_prices() -> List[dict]:
    """
    Returns live prices for all supported cryptos.
    Fetches all prices in a single batch from Redis.
    Sets default values for missing keys with expiry.
    """
    result: List[dict] = []

    redis = await get_redis()

    with SessionLocal() as db:
        cryptos = db.query(Crypto).all()
        if not cryptos:
            return result

        keys = [f"crypto:{crypto.binance_symbol.lower()}" for crypto in cryptos]
        data_list = await redis.mget(*keys)

        missing_defaults = {}
        for crypto, data in zip(cryptos, data_list):
            price = 0.0
            change_pct = "0%"
            market_cap = 0.0

            if data:
                try:
                    data_json = json.loads(data)
                    price = float(data_json.get("c", 0))
                    change_pct = data_json.get("P", "0%")
                    market_cap = float(data_json.get("market_cap", 0))
                except (json.JSONDecodeError, ValueError):
                    pass
            else:
                key = f"crypto:{crypto.binance_symbol.lower()}"
                missing_defaults[key] = json.dumps({"c": 0, "P": "0%", "market_cap": 0})

            result.append({
                "name": crypto.name,
                "symbol": crypto.universal_symbol,
                "binance_symbol": crypto.binance_symbol,
                "price": price,
                "change": change_pct,
                "market_cap": market_cap
            })

        if missing_defaults:
            pipe = redis.pipeline()
            for k, v in missing_defaults.items():
                pipe.set(k, v, ex=30)
            await pipe.execute()

    return result

# ==============================
# Historical candle data
# ==============================
async def get_crypto_history(symbol: str, time_range: str = "1M") -> Optional[List[dict]]:
    """
    Returns historical OHLC/candle data for a crypto.
    First checks Redis cache, else generates mock fallback data and caches it.
    """
    # 1️⃣ Try to get from cache
    cached = await cache_get_history(symbol)
    if cached:
        return cached.get("candles")

    # 2️⃣ Fallback: generate mock candle data
    num_points = {
        "1D": 24, "7D": 7, "1M": 30, "3M": 90,
        "6M": 180, "1Y": 365, "3Y": 365*3, "5Y": 365*5, "ALL": 365
    }.get(time_range, 30)

    now = datetime.utcnow()
    candles = []
    price = 100 + random.random() * 20
    for i in reversed(range(num_points)):
        ts = now - timedelta(days=i)
        close = price + random.uniform(-5, 5)
        candles.append({"time": int(ts.timestamp() * 1000), "close": round(close, 2)})

    # 3️⃣ Cache generated data for future use
    await cache_set_history(symbol, candles)

    return candles