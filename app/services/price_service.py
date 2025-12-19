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
                    # Calculate market_cap from circulating_supply if not in Redis
                    market_cap = float(data_json.get("market_cap", 0)) or \
                                 price * getattr(crypto, "circulating_supply", 0)
                except (json.JSONDecodeError, ValueError):
                    pass
            else:
                # Use last known price if available, else default to 0
                last_price = getattr(crypto, "last_known_price", 0)
                key = f"crypto:{crypto.binance_symbol.lower()}"
                missing_defaults[key] = json.dumps({
                    "c": last_price,
                    "P": "0%",
                    "market_cap": last_price * getattr(crypto, "circulating_supply", 0)
                })
                price = last_price
                market_cap = price * getattr(crypto, "circulating_supply", 0)

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
RANGE_DAYS = {
    "1D": 1,
    "7D": 7,
    "1M": 30,
    "3M": 90,
    "6M": 180,
    "1Y": 365,
    "3Y": 365*3,
    "5Y": 365*5,
    "ALL": 365
}

async def get_crypto_history(symbol: str, time_range: str = "1M") -> Optional[List[dict]]:
    """
    Returns historical OHLC/candle data for a crypto.
    Full history is cached; returned data is sliced according to `time_range`.
    """
    redis = await get_redis()
    cache_key = f"crypto_history:{symbol.upper()}"
    cached = await cache_get_history(cache_key)  # full history

    if cached:
        full_candles = cached.get("candles", [])
    else:
        # fallback: generate full mock history (max 5Y)
        full_candles = []
        now = datetime.utcnow()
        price = 100 + random.random() * 20
        for i in reversed(range(RANGE_DAYS.get("5Y", 1825))):
            ts = now - timedelta(days=i)
            close = price + random.uniform(-5, 5)
            full_candles.append({"time": int(ts.timestamp() * 1000), "close": round(close, 2)})

        # cache full history
        await cache_set_history(cache_key, full_candles)

    # slice according to requested range
    n_days = RANGE_DAYS.get(time_range, 30)
    candles = full_candles[-n_days:] if n_days < len(full_candles) else full_candles

    return candles