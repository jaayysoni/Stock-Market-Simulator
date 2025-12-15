# app/utils/cache.py
import json
from typing import Any, Optional
from app.utils.redis_client import get_redis

# =========================
# Generic cache helpers
# =========================

async def set_cached_data(key: str, data: Any, ttl: int = 30):
    """Cache data as JSON in Redis."""
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

CRYPTO_PRICE_CACHE_KEY = "crypto:prices:all"
CRYPTO_PRICE_TTL = 5  # seconds, adjust as needed

async def set_crypto_prices(data: Any):
    """Cache all crypto prices."""
    await set_cached_data(
        key=CRYPTO_PRICE_CACHE_KEY,
        data=data,
        ttl=CRYPTO_PRICE_TTL
    )


async def get_crypto_prices() -> Optional[Any]:
    """Get cached crypto prices."""
    return await get_cached_data(CRYPTO_PRICE_CACHE_KEY)


async def invalidate_crypto_prices():
    """Force refresh of crypto prices."""
    await delete_cached_data(CRYPTO_PRICE_CACHE_KEY)