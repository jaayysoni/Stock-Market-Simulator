"""
Local real-time stock price updater.
- BSE, NSE, BANKNIFTY: yfinance (batch)
- Other stocks: Finnhub WebSocket
- Redis cache: latest price + intraday history
"""

import os
import json
import asyncio
import websockets
import redis.asyncio as aioredis
import yfinance as yf
from datetime import datetime, timezone
from dotenv import load_dotenv
from app.config import settings

# Load environment variables
load_dotenv()

FINNHUB_WS = f"wss://ws.finnhub.io?token={settings.FINNHUB_API_KEY}"

# Redis client (local)
redis = aioredis.from_url("redis://localhost:6379/0", decode_responses=True)

# Indices via yfinance
INDICES = {
    "BSE": "^BSESN",
    "NSE": "^NSEI",
    "BANKNIFTY": "^NSEBANK"
}

# -----------------------------
# YFinance fetcher for indices
# -----------------------------
async def fetch_index_prices():
    while True:
        try:
            for name, symbol in INDICES.items():
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d", interval="1m")
                if not data.empty:
                    price = float(data["Close"].iloc[-1])
                    payload = {
                        "symbol": name,
                        "price": price,
                        "ts": datetime.now(timezone.utc).isoformat()
                    }
                    # Store in Redis
                    await redis.set(f"stock:{name}:latest", json.dumps(payload))
                    await redis.zadd(f"stock:{name}:history", {json.dumps(payload): datetime.now(timezone.utc).timestamp()})
                    await redis.publish("stocks:updates", json.dumps(payload))
            await asyncio.sleep(10)  # refresh indices every 10s
        except Exception as e:
            print(f"⚠️ Error fetching index prices: {e}")
            await asyncio.sleep(30)

# -----------------------------
# Finnhub WebSocket handler
# -----------------------------
async def finnhub_ws_handler(active_stocks=None):
    if active_stocks is None:
        active_stocks = ["TCS.NS", "INFY.NS", "RELIANCE.NS"]  # default local test

    while True:
        try:
            async with websockets.connect(FINNHUB_WS, ping_interval=20, ping_timeout=20) as ws:
                print("✅ Connected to Finnhub WebSocket")

                # Subscribe to stocks
                for symbol in active_stocks:
                    await ws.send(json.dumps({"type": "subscribe", "symbol": symbol}))
                    print(f"✅ Subscribed to {symbol}")

                # Listen for messages
                async for msg in ws:
                    data = json.loads(msg)
                    if data.get("type") == "ping":
                        continue
                    if data.get("type") == "trade":
                        for trade in data.get("data", []):
                            payload = {
                                "symbol": trade["s"],
                                "price": trade["p"],
                                "ts": datetime.fromtimestamp(trade["t"] / 1000, tz=timezone.utc).isoformat()
                            }
                            # Store in Redis
                            await redis.set(f"stock:{trade['s']}:latest", json.dumps(payload))
                            await redis.zadd(f"stock:{trade['s']}:history", {json.dumps(payload): trade["t"] / 1000})
                            await redis.publish("stocks:updates", json.dumps(payload))
        except Exception as e:
            print(f"⚠️ Finnhub WS error: {e}, reconnecting in 5s...")
            await asyncio.sleep(5)

# -----------------------------
# Entry point
# -----------------------------
async def start_price_updater():
    await asyncio.gather(
        fetch_index_prices(),
        finnhub_ws_handler()
    )

if __name__ == "__main__":
    asyncio.run(start_price_updater())