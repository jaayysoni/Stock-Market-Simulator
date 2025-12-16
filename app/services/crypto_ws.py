# app/services/crypto_ws.py

import asyncio
import json
import websockets
from typing import List

from app.config import settings
from app.database.db import SessionLocal
from app.models.crypto import Crypto
from app.utils.cache import set_cached_data


# =========================
# SINGLE CRYPTO WS
# =========================

class SingleCryptoWebSocket:
    def __init__(self, symbol: str):
        self.symbol = symbol.lower()
        self.ws_url = settings.BINANCE_WS_URL

    async def run(self):
        """
        Runs ONE websocket for ONE crypto forever
        """
        url = f"{self.ws_url}/ws/{self.symbol}@ticker"
        print(f"🚀 WS connecting: {self.symbol.upper()}")

        while True:
            try:
                async with websockets.connect(
                    url,
                    ping_interval=20,
                    ping_timeout=20
                ) as ws:
                    print(f"✅ WS connected: {self.symbol.upper()}")

                    async for msg in ws:
                        data = json.loads(msg)

                        # Binance ticker payload contains "s" (symbol)
                        if "s" not in data:
                            continue

                        symbol = data["s"].lower()
                        key = f"crypto:{symbol}"

                        await set_cached_data(
                            key,
                            data,
                            ttl=10
                        )

            except Exception as e:
                print(f"⚠️ WS reconnecting ({self.symbol}):", e)
                await asyncio.sleep(5)


# =========================
# WS MANAGER
# =========================

class CryptoWebSocketManager:
    def __init__(self, symbols: List[str]):
        self.symbols = [s.lower() for s in symbols]

    async def start(self):
        """
        Starts ONE websocket per crypto
        """
        tasks = []

        for symbol in self.symbols:
            ws = SingleCryptoWebSocket(symbol)
            tasks.append(asyncio.create_task(ws.run()))

        print(f"🚀 Binance WS started for {len(tasks)} cryptos (1 WS per crypto)")
        await asyncio.gather(*tasks)


# =========================
# STARTUP HELPERS
# =========================

def get_all_binance_symbols() -> List[str]:
    """
    Load ALL Binance symbols from DB (must be 90)
    """
    db = SessionLocal()
    try:
        symbols = db.query(Crypto.binance_symbol).all()
        symbol_list = [s[0].lower() for s in symbols]
        print("📦 Loaded symbols from DB:", len(symbol_list))
        return symbol_list
    finally:
        db.close()


crypto_ws_manager: CryptoWebSocketManager | None = None


async def start_crypto_ws():
    """
    Called ONCE on FastAPI startup
    """
    global crypto_ws_manager

    symbols = get_all_binance_symbols()
    if not symbols:
        raise RuntimeError("❌ No crypto symbols found in DB")

    crypto_ws_manager = CryptoWebSocketManager(symbols)

    # Run all websockets in background
    asyncio.create_task(crypto_ws_manager.start())