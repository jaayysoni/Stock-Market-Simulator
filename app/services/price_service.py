# app/services/price_service.py
import json
from typing import List
from app.database.db import SessionLocal
from app.models.crypto import Crypto
from app.utils.redis_client import get_redis


async def get_all_crypto_prices() -> List[dict]:
    """
    Returns live prices for all supported cryptos.
    Fetches all prices in a single batch from Redis.
    Sets default values for missing keys with expiry.
    """
    result: List[dict] = []

    # Get Redis client
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
            market_cap = 0.0  # optional, if stored in Redis

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

        # Batch set missing defaults with 30s expiry
        if missing_defaults:
            pipe = redis.pipeline()
            for k, v in missing_defaults.items():
                pipe.set(k, v, ex=30)
            await pipe.execute()

    return result