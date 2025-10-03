import os
import redis.asyncio as redis  # updated import for asyncio support

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

async def set_data(key: str, value: dict, expire: int = 30):
    await redis_client.set(key, str(value), ex=expire)

async def get_data(key: str):
    data = await redis_client.get(key)
    return eval(data) if data else None