import asyncio
import json
import websockets
from app.config import BINANCE_WS_URL
from app.utils.cache import set_cached_data

class CryptoWebSocket:
    def __init__(self, symbols: list[str]):
        self.symbols = [s.lower() for s in symbols]  # normalize symbols
        self.ws_url = BINANCE_WS_URL
        self.keep_running = True

    def _build_url(self) -> str:
        streams = [f"{s}@ticker" for s in self.symbols]
        return f"{self.ws_url}/stream?streams={'/'.join(streams)}"

    async def _connect(self):
        url = self._build_url()
        async with websockets.connect(url) as ws:
            print("✅ Connected to Binance WebSocket")
            while self.keep_running:
                try:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    # Binance returns {"stream": "...", "data": {...}}
                    if "data" in data and "s" in data["data"]:
                        symbol = data["data"]["s"].lower()  # BTCUSDT -> btcusdt
                        await set_cached_data(f"crypto:{symbol}", data["data"], ttl=5)
                except Exception as e:
                    print("⚠️ WebSocket error:", e)
                    await asyncio.sleep(1)

    async def start(self):
        """Reconnect loop if connection drops"""
        while True:
            try:
                await self._connect()
            except Exception as e:
                print("⚠️ Connection lost, reconnecting in 5s...", e)
                await asyncio.sleep(5)