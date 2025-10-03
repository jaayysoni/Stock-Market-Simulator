# app/tasks/market_tasks.py
import asyncio
import yfinance as yf
from app.utils.cache import get_redis
import json

async def refresh_market_indices():
    """
    Refresh BSE, NSE, Bank Nifty prices every 60 seconds.
    Store them in Redis as a hash.
    """
    redis_client = await get_redis()
    
    while True:
        try:
            bse = yf.Ticker("^BSESN").info
            nse = yf.Ticker("^NSEI").info
            bank_nifty = yf.Ticker("^NSEBANK").info
            
            await redis_client.hset("market_indices", mapping={
                "BSE_price": bse.get("regularMarketPrice"),
                "BSE_change": bse.get("regularMarketChangePercent"),
                "NSE_price": nse.get("regularMarketPrice"),
                "NSE_change": nse.get("regularMarketChangePercent"),
                "BankNifty_price": bank_nifty.get("regularMarketPrice"),
                "BankNifty_change": bank_nifty.get("regularMarketChangePercent"),
            })
        except Exception as e:
            print("Error refreshing market indices:", e)
        
        await asyncio.sleep(60)  # refresh every 60s


async def refresh_top_movers():
    """
    Refresh top 4 gainers and top 4 losers every 60 seconds.
    Store them in Redis as JSON strings.
    """
    redis_client = await get_redis()
    symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"]  # example top stocks

    while True:
        try:
            data = []
            for sym in symbols:
                try:
                    stock = yf.Ticker(sym).info
                    data.append({
                        "symbol": sym,
                        "price": stock.get("regularMarketPrice"),
                        "change": stock.get("regularMarketChangePercent")
                    })
                except Exception as e:
                    print(f"Error fetching {sym}: {e}")
                    continue

            # Sort top 4 gainers
            gainers = sorted(data, key=lambda x: x["change"] or 0, reverse=True)[:4]
            # Sort top 4 losers
            losers = sorted(data, key=lambda x: x["change"] or 0)[:4]

            await redis_client.set("top_gainers", json.dumps(gainers))
            await redis_client.set("top_losers", json.dumps(losers))
        except Exception as e:
            print("Error refreshing top movers:", e)

        await asyncio.sleep(30)  # refresh every 30s