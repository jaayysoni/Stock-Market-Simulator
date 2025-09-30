# app/utils/cache.py
import redis.asyncio as redis
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_redis_client: redis.Redis | None = None

async def get_redis() -> redis.Redis:
    """
    Returns a singleton Redis client.
    Usage: 
        r = await get_redis()
        await r.set("key", "value")
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client