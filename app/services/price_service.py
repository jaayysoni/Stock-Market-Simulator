# app/services/price_service.py

import json
from typing import List
from app.database.db import SessionLocal
from app.models.crypto import Crypto
from app.utils.redis_client import redis  # direct access to Redis


async def get_all_crypto_prices() -> List[dict]:
    """
    Returns live prices for all supported cryptos.
    Reads directly from WebSocket cache in Redis.
    """

    db = SessionLocal()
    try:
        cryptos = db.query(Crypto).all()
        result: List[dict] = []

        for crypto in cryptos:
            key = f"crypto:{crypto.binance_symbol.lower()}"
            data = await redis.get(key)
            if not data:
                # Price not yet cached; skip silently
                continue

            try:
                data_json = json.loads(data)
                price = float(data_json.get("c", 0))  # 'c' = current price in Binance ticker
            except (json.JSONDecodeError, ValueError):
                # Malformed cache data; skip
                continue

            result.append({
                "name": crypto.name,
                "symbol": crypto.universal_symbol,
                "binance_symbol": crypto.binance_symbol,
                "price": price,
            })

        return result

    finally:
        db.close()