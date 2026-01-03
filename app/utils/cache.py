# app/utils/cache.py
import json
from typing import Any, Optional
from datetime import datetime
from app.utils.redis_client import get_redis  # async access only
import logging

logger = logging.getLogger(__name__)

# =========================
# Key prefixes
# =========================
SYMBOL_KEY_PREFIX = "CRYPTO:SYMBOL:"    # per-symbol WS cache
ALL_PRICES_KEY = "CRYPTO:PRICES:ALL"   # aggregated snapshot for dashboard
ALL_PRICES_TTL = 5                      # seconds

# =========================
# Generic cache helpers
# =========================
async def set_cached_data(key: str, data: Any, ttl: int = 30):
    """Cache data as JSON in Redis with optional TTL in seconds."""
    r = await get_redis()
    await r.set(key, json.dumps(data), ex=ttl)
    logger.debug(f"Redis SET key={key} ttl={ttl}")

async def get_cached_data(key: str) -> Optional[Any]:
    """Retrieve cached JSON data from Redis."""
    r = await get_redis()
    data = await r.get(key)
    if data:
        logger.debug(f"Redis HIT key={key}")
    else:
        logger.debug(f"Redis MISS key={key}")
    return json.loads(data) if data else None

async def delete_cached_data(key: str):
    """Delete a cache key."""
    r = await get_redis()
    await r.delete(key)
    logger.debug(f"Redis DEL key={key}")

# =========================
# Per-symbol WS cache
# =========================
async def set_symbol_price(symbol: str, data: Any, ttl: int = 10):
    """Cache live price for a single symbol (from WebSocket)."""
    key = f"{SYMBOL_KEY_PREFIX}{symbol.upper()}"
    await set_cached_data(key, data, ttl=ttl)

async def get_symbol_price(symbol: str) -> Optional[Any]:
    """Retrieve live price for a single symbol from cache."""
    key = f"{SYMBOL_KEY_PREFIX}{symbol.upper()}"
    return await get_cached_data(key)

async def invalidate_symbol_price(symbol: str):
    """Delete cached WS price for a given symbol."""
    key = f"{SYMBOL_KEY_PREFIX}{symbol.upper()}"
    await delete_cached_data(key)

# =========================
# Global snapshot cache (all cryptos for dashboard)
# =========================
async def set_crypto_prices(data: Any):
    """Cache snapshot of all crypto prices (for dashboard)."""
    await set_cached_data(ALL_PRICES_KEY, data, ttl=ALL_PRICES_TTL)

async def get_crypto_prices() -> Optional[Any]:
    """Get cached snapshot of all crypto prices."""
    return await get_cached_data(ALL_PRICES_KEY)

async def invalidate_crypto_prices():
    """Force refresh of global crypto prices."""
    await delete_cached_data(ALL_PRICES_KEY)