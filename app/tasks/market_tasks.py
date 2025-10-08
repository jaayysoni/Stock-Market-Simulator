# app/tasks/market_tasks.py
import asyncio
import yfinance as yf
import json
from app.utils.cache import get_redis
from app.services.stock_service import load_nse_top_500

TOP_GAINERS_KEY = "top_gainers"
TOP_LOSERS_KEY = "top_losers"
MARKET_INDICES_KEY = "market_indices"

INDICES_REFRESH_INTERVAL = 150
TOP_MOVERS_REFRESH_INTERVAL = 120

async def fetch_stock_info(symbol: str):
    try:
        info = await asyncio.to_thread(lambda: yf.Ticker(symbol).info)
        return {
            "symbol": symbol,
            "price": info.get("regularMarketPrice"),
            "change": info.get("regularMarketChangePercent") or 0
        }
    except Exception:
        return None

async def refresh_market_indices():
    redis_client = await get_redis()
    while True:
        try:
            bse, nse, bank_nifty = await asyncio.gather(
                fetch_stock_info("^BSESN"),
                fetch_stock_info("^NSEI"),
                fetch_stock_info("^NSEBANK")
            )
            await redis_client.hset(MARKET_INDICES_KEY, mapping={
                "BSE_price": bse["price"],
                "BSE_change": bse["change"],
                "NSE_price": nse["price"],
                "NSE_change": nse["change"],
                "BankNifty_price": bank_nifty["price"],
                "BankNifty_change": bank_nifty["change"],
            })
        except Exception as e:
            print("Error refreshing market indices:", e)
        await asyncio.sleep(INDICES_REFRESH_INTERVAL)

async def refresh_top_movers():
    redis_client = await get_redis()
    symbols = [s + ".NS" for s in load_nse_top_500()]

    while True:
        try:
            # Fetch stock info concurrently in batches
            tasks = [fetch_stock_info(sym) for sym in symbols]
            results = await asyncio.gather(*tasks)

            data = [r for r in results if r is not None]

            gainers = sorted(data, key=lambda x: x["change"], reverse=True)[:4]
            losers = sorted(data, key=lambda x: x["change"])[:4]

            await redis_client.set(TOP_GAINERS_KEY, json.dumps(gainers))
            await redis_client.set(TOP_LOSERS_KEY, json.dumps(losers))
        except Exception as e:
            print("Error refreshing top movers:", e)
        await asyncio.sleep(TOP_MOVERS_REFRESH_INTERVAL)