# app/utils/redis_client.py
import os
from redis.asyncio import Redis, from_url

# =========================
# Configuration from environment
# =========================
REDIS_URL = os.getenv("REDIS_URL")  # must be set on Render
if not REDIS_URL:
    # fallback for local development
    REDIS_URL = "redis://localhost:6379"

REDIS_DEFAULT_DB = int(os.getenv("REDIS_DB", 0))  # optional separate DB for crypto cache

# Internal singleton Redis instance
_redis_client: Redis | None = None


async def get_redis() -> Redis:
    """
    Initialize and return a Redis async connection.
    Uses connection pooling internally.
    Reuses the same connection for multiple calls.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = from_url(
            REDIS_URL,
            decode_responses=True,
            db=REDIS_DEFAULT_DB,
            max_connections=20,  # allow multiple concurrent connections
        )
    return _redis_client


async def close_redis():
    """
    Close the Redis connection if it exists.
    """
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        _redis_client = None