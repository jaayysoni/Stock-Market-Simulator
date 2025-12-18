# app/utils/cache.py
import json
from typing import Any, Optional
from datetime import datetime
from app.utils.redis_client import get_redis  # only use get_redis for async access

HISTORY_KEY_PREFIX = "CRYPTO:HISTORY:"

# =========================
# Generic cache helpers
# =========================

async def set_cached_data(key: str, data: Any, ttl: int = 30):
    """Cache data as JSON in Redis with optional TTL in seconds."""
    r = await get_redis()
    await r.set(key, json.dumps(data), ex=ttl)

async def get_cached_data(key: str) -> Optional[Any]:
    """Retrieve cached JSON data from Redis."""
    r = await get_redis()
    data = await r.get(key)
    if data:
        return json.loads(data)
    return None

async def delete_cached_data(key: str):
    """Delete a cache key."""
    r = await get_redis()
    await r.delete(key)

# =========================
# Crypto price cache helpers
# =========================

CRYPTO_PRICE_CACHE_KEY = "CRYPTO:PRICES:ALL"
CRYPTO_PRICE_TTL = 5  # seconds

async def set_crypto_prices(data: Any):
    """Cache all crypto prices."""
    await set_cached_data(CRYPTO_PRICE_CACHE_KEY, data, ttl=CRYPTO_PRICE_TTL)

async def get_crypto_prices() -> Optional[Any]:
    """Get cached crypto prices."""
    return await get_cached_data(CRYPTO_PRICE_CACHE_KEY)

async def invalidate_crypto_prices():
    """Force refresh of crypto prices."""
    await delete_cached_data(CRYPTO_PRICE_CACHE_KEY)

# =========================
# Crypto history cache helpers
# =========================

async def set_crypto_history(symbol: str, candles: list):
    """Cache historical data for a crypto symbol."""
    key = f"{HISTORY_KEY_PREFIX}{symbol.upper()}"
    payload = {
        "symbol": symbol.upper(),
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
        "candles": candles
    }
    r = await get_redis()
    await r.set(key, json.dumps(payload))

async def get_crypto_history(symbol: str) -> Optional[Any]:
    """Retrieve cached historical data for a crypto symbol."""
    key = f"{HISTORY_KEY_PREFIX}{symbol.upper()}"
    r = await get_redis()
    data = await r.get(key)
    if not data:
        return None
    return json.loads(data)

async def invalidate_crypto_history(symbol: str):
    """Delete cached history for a given symbol."""
    key = f"{HISTORY_KEY_PREFIX}{symbol.upper()}"
    r = await get_redis()
    await r.delete(key)