# app/utils/redis_client.py
import os
from redis.asyncio import Redis, from_url

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

_redis_client: Redis | None = None  # internal singleton


async def get_redis() -> Redis:
    """
    Initialize and return a Redis connection.
    Reuses the same connection for multiple calls.
    """
    global _redis_client
    if not _redis_client:
        _redis_client = from_url(REDIS_URL, decode_responses=True)
    return _redis_client


async def close_redis():
    """
    Close Redis connection if it exists.
    """
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None


# Optional convenience shortcut (always use get_redis() for safety)
# redis: Redis | None = _redis_client  # not recommended directly, may be None