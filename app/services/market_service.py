# app/services/market_service.py
import aiohttp
import json
from app.utils.cache import get_redis

TOP_GAINERS_KEY = "top_gainers"
TOP_LOSERS_KEY = "top_losers"
CACHE_TTL = 120  # seconds

async def fetch_top_movers():
    redis_client = await get_redis()
    
    # Step 1: Get cookies
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.nseindia.com", headers={"User-Agent": "Mozilla/5.0"}) as r:
            cookies = r.cookies

        # Step 2: Fetch top movers
        url = "https://www.nseindia.com/api/live-analysis-variations"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com/"
        }

        async with session.get(url, headers=headers, cookies=cookies) as resp:
            if resp.status != 200:
                print("Failed to fetch top movers:", resp.status)
                return
            data = await resp.json()

    all_stocks = data.get("data", [])

    # Step 3: Sort gainers and losers
    gainers = sorted(all_stocks, key=lambda x: float(x["changePercent"]), reverse=True)[:4]
    losers = sorted(all_stocks, key=lambda x: float(x["changePercent"]))[:4]

    # Step 4: Cache in Redis
    await redis_client.set(TOP_GAINERS_KEY, json.dumps(gainers), ex=CACHE_TTL)
    await redis_client.set(TOP_LOSERS_KEY, json.dumps(losers), ex=CACHE_TTL)