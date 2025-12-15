import json
from typing import Any, Optional
from app.utils.redis_client import redis

async def set_cached_data(key: str, data: Any, ttl: int = 30):
    """Cache data as JSON in Redis."""
    await redis.set(key, json.dumps(data), ex=ttl)

async def get_cached_data(key: str) -> Optional[Any]:
    """Retrieve cached JSON data from Redis."""
    data = await redis.get(key)
    if data:
        return json.loads(data)
    return None