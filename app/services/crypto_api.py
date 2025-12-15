import aiohttp
from app.utils.cache import get_cached_data, set_cached_data

BINANCE_REST_URL = "https://api.binance.com/api/v3/ticker/price"

async def fetch_price(symbol: str) -> float:
    """Fetch price from cache first, fallback to REST API."""
    key = f"crypto:{symbol.lower()}"
    cached = await get_cached_data(key)
    if cached:
        return float(cached['c'])  # current price
    # fallback
    async with aiohttp.ClientSession() as session:
        async with session.get(BINANCE_REST_URL, params={"symbol": symbol.upper()}) as resp:
            data = await resp.json()
            await set_cached_data(key, data, ttl=5)
            return float(data['price'])
        