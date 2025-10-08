# app/tasks/nifty_tasks.py

import asyncio
import json
from datetime import date
import pandas as pd
from nsepy import get_history
from app.utils.cache import get_redis

# ----------------- Constants -----------------
NIFTY_SYMBOL = "NIFTY"
CACHE_KEY = "nifty50_historical"
LATEST_PRICE_KEY = "nifty50_latest"
REFRESH_INTERVAL = 3600  # 1 hour

# ----------------- Fetch Historical Nifty -----------------
async def fetch_nifty_historical():
    """
    Fetch historical Nifty 50 data using NSEPY.
    Returns list of {"date": ..., "close": ...}
    """
    data = get_history(
        symbol=NIFTY_SYMBOL,
        index=True,
        start=date(2023, 1, 1),  # Change start date as needed
        end=date.today()
    )

    df = pd.DataFrame(data)
    df.reset_index(inplace=True)  # Make 'Date' a column

    historical_data = [{"date": str(row["Date"].date()), "close": float(row["Close"])} for _, row in df.iterrows()]
    return historical_data

# ----------------- Fetch Latest Nifty -----------------
async def fetch_nifty_latest():
    """
    Get latest Nifty price from NSEPY historical data (last row).
    """
    data = get_history(
        symbol=NIFTY_SYMBOL,
        index=True,
        start=date.today(),
        end=date.today()
    )
    if not data.empty:
        last_row = data.iloc[-1]
        return {"price": float(last_row["Close"]), "change": float(last_row["Close"] - last_row["Prev Close"])}
    return {"price": 0, "change": 0}

# ----------------- Refresh Redis Cache -----------------
async def refresh_nifty_cache():
    redis_client = await get_redis()
    while True:
        try:
            historical_data = await fetch_nifty_historical()
            latest_price = await fetch_nifty_latest()
            await redis_client.set(CACHE_KEY, json.dumps(historical_data), ex=86400)  # 1 day
            await redis_client.set(LATEST_PRICE_KEY, json.dumps(latest_price), ex=300)  # 5 min
            print(f"🟢 Nifty cache updated: {len(historical_data)} points, latest price {latest_price['price']}")
        except Exception as e:
            print(f"❌ Failed to refresh Nifty cache: {e}")
        await asyncio.sleep(REFRESH_INTERVAL)

# ----------------- Get Cached Historical -----------------
async def get_cached_nifty_history(days: int = 30):
    redis_client = await get_redis()
    cached = await redis_client.get(CACHE_KEY)
    if cached:
        data = json.loads(cached)
    else:
        print("⚠️ Redis cache empty, fetching Nifty historical live")
        data = await fetch_nifty_historical()
        await redis_client.set(CACHE_KEY, json.dumps(data), ex=86400)

    if days:
        data = data[-days:]
    dates = [d["date"] for d in data]
    prices = [d["close"] for d in data]
    return {"dates": dates, "prices": prices}

# ----------------- Get Cached Latest -----------------
async def get_cached_nifty_latest():
    redis_client = await get_redis()
    cached = await redis_client.get(LATEST_PRICE_KEY)
    if cached:
        return json.loads(cached)
    print("⚠️ Redis cache empty, fetching Nifty latest live")
    latest = await fetch_nifty_latest()
    await redis_client.set(LATEST_PRICE_KEY, json.dumps(latest), ex=300)
    return latest