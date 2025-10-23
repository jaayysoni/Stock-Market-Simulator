# app/services/finnhub_client.py

import os
import asyncio
import json
import websockets
import logging
from dotenv import load_dotenv
from app.utils.cache import get_redis

# Load environment variables from .env file
load_dotenv()

# Load Finnhub API key
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
if not FINNHUB_API_KEY:
    raise ValueError("FINNHUB_API_KEY is not set in environment or .env file")

FINNHUB_WS_URL = f"wss://ws.finnhub.io?token={FINNHUB_API_KEY}"

# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinnhubWebSocket")


class FinnhubWebSocketClient:
    """
    Finnhub WebSocket client to fetch real-time NSE Top 500 stock prices.
    Features:
        - Dynamic subscribe/unsubscribe per stock symbol
        - Store latest price and last 100 history points in Redis
        - Publish updates to Redis channel 'stocks:updates' for WebSocket broadcasting
        - Auto-reconnect on connection failure
    """

    def __init__(self):
        self.ws: websockets.WebSocketClientProtocol | None = None
        self.subscribed_symbols: set[str] = set()
        self.redis = None
        self.lock = asyncio.Lock()  # Ensure only one message is sent at a time

    async def connect(self):
        """
        Main connection loop. Automatically reconnects on disconnect.
        """
        self.redis = await get_redis()  # Redis client
        while True:
            try:
                async with websockets.connect(FINNHUB_WS_URL) as websocket:
                    self.ws = websocket
                    logger.info("✅ Connected to Finnhub WebSocket")

                    # Resubscribe to previously subscribed symbols
                    for symbol in self.subscribed_symbols.copy():
                        await self.subscribe(symbol)

                    await self.listen()
            except Exception as e:
                logger.error(f"⚠️ WebSocket error: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

    async def listen(self):
        """
        Listen for incoming messages from Finnhub.
        """
        async for message in self.ws:
            try:
                data = json.loads(message)
                if "data" in data:
                    for item in data["data"]:
                        symbol = item["s"]
                        price = item["p"]
                        ts = item["t"]

                        # Save latest price and last 100 points in Redis
                        await self.redis.set(f"stock:{symbol}:latest", price)
                        await self.redis.lpush(
                            f"stock:{symbol}:history",
                            json.dumps({"t": ts, "p": price})
                        )
                        await self.redis.ltrim(f"stock:{symbol}:history", 0, 99)

                        # Publish to channel for frontend WebSocket clients
                        await self.redis.publish(
                            "stocks:updates",
                            json.dumps({"symbol": symbol, "price": price, "timestamp": ts})
                        )
            except Exception as err:
                logger.error(f"Error processing message: {err}")

    async def subscribe(self, symbol: str):
        """
        Subscribe to a stock symbol for live updates.
        """
        async with self.lock:
            if symbol not in self.subscribed_symbols and self.ws:
                msg = {"type": "subscribe", "symbol": symbol}
                await self.ws.send(json.dumps(msg))
                self.subscribed_symbols.add(symbol)
                logger.info(f"📈 Subscribed: {symbol}")

    async def unsubscribe(self, symbol: str):
        """
        Unsubscribe from a stock symbol to stop receiving updates.
        """
        async with self.lock:
            if symbol in self.subscribed_symbols and self.ws:
                msg = {"type": "unsubscribe", "symbol": symbol}
                await self.ws.send(json.dumps(msg))
                self.subscribed_symbols.remove(symbol)
                logger.info(f"📉 Unsubscribed: {symbol}")


# Singleton instance (remove trailing comma)
finnhub_client = FinnhubWebSocketClient()