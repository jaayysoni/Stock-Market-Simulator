# app/utils/redis_client.py
import os
from redis.asyncio import Redis, from_url

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client: Redis | None = None  # type hint fixed

async def get_redis() -> Redis:
    """Initialize and return a Redis connection."""
    global redis_client
    if not redis_client:
        redis_client = from_url(REDIS_URL, decode_responses=True)
    return redis_client

async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None

# Expose redis for convenience in cache.py
redis: Redis | None = redis_client