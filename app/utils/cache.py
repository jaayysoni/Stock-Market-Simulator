# app/utils/cache.py
import os
import json
import redis.asyncio as redis
from typing import Optional, Any
from datetime import timedelta

# ======================================================
# ⚙️ Redis Configuration
# ======================================================

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
DEFAULT_STOCK_CACHE_EXPIRY = int(os.getenv("STOCK_CACHE_TTL", 60))  # 60 sec default

_redis_client: Optional[redis.Redis] = None  # Singleton instance


# ======================================================
# 🔌 Redis Connection
# ======================================================

async def get_redis() -> redis.Redis:
    """Return a singleton Redis client instance."""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                encoding="utf-8"
            )
        except Exception as e:
            print(f"⚠️ Failed to connect to Redis: {e}")
            raise
    return _redis_client


# ======================================================
# 💾 Basic Cache Operations
# ======================================================

async def cache_set(key: str, value: Any, expire_seconds: int = 1800) -> None:
    """Store a value in Redis with expiration (default 30 min)."""
    try:
        redis_client = await get_redis()
        if not isinstance(value, str):
            value = json.dumps(value)  # serialize complex data
        await redis_client.set(key, value, ex=expire_seconds)
    except Exception as e:
        print(f"⚠️ Redis SET failed for key '{key}': {e}")


async def cache_get(key: str) -> Optional[Any]:
    """Retrieve cached value by key. Returns None if unavailable."""
    try:
        redis_client = await get_redis()
        value = await redis_client.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)  # try to parse JSON
        except json.JSONDecodeError:
            return value
    except Exception as e:
        print(f"⚠️ Redis GET failed for key '{key}': {e}")
        return None


async def cache_delete(key: str) -> None:
    """Delete a key from Redis cache."""
    try:
        redis_client = await get_redis()
        await redis_client.delete(key)
    except Exception as e:
        print(f"⚠️ Redis DELETE failed for key '{key}': {e}")


async def close_redis() -> None:
    """Gracefully close Redis connection (for FastAPI shutdown)."""
    global _redis_client
    if _redis_client:
        try:
            await _redis_client.close()
            _redis_client = None
            print("✅ Redis connection closed.")
        except Exception as e:
            print(f"⚠️ Redis close failed: {e}")


# ======================================================
# 📈 Stock Price Caching Helpers
# ======================================================

async def get_cached_stock(symbol: str) -> Optional[Any]:
    """
    Retrieve cached stock data.
    Returns None if not found or expired.
    """
    key = f"stock:{symbol.upper()}"
    return await cache_get(key)


async def set_cached_stock(symbol: str, data: Any, ttl: Optional[int] = None) -> None:
    """
    Cache stock data for a given symbol.
    Default expiry = STOCK_CACHE_TTL (env) or 60 seconds.
    """
    key = f"stock:{symbol.upper()}"
    expire_seconds = ttl or DEFAULT_STOCK_CACHE_EXPIRY
    await cache_set(key, data, expire_seconds)