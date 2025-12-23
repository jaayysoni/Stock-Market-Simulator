# app/services/crypto_ws.py

import asyncio
import json
import websockets
from typing import List

from app.config import settings
from app.database.db import SessionLocal
from app.models.crypto import Crypto
from app.utils.cache import set_symbol_price, get_crypto_prices, set_crypto_prices

# =========================
# SINGLE CRYPTO WS
# =========================

class SingleCryptoWebSocket:
    def __init__(self, symbol: str):
        self.symbol = symbol.lower()
        self.ws_url = settings.BINANCE_WS_URL  # e.g., "wss://stream.binance.com:9443"

    async def run(self):
        url = f"{self.ws_url}/ws/{self.symbol}@ticker"
        print(f"🚀 WS connecting: {self.symbol.upper()}")

        while True:
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                    print(f"✅ WS connected: {self.symbol.upper()}")
                    async for msg in ws:
                        try:
                            data = json.loads(msg)
                            if "s" not in data:
                                continue

                            symbol_upper = data["s"].upper()

                            # Cache per-symbol
                            await set_symbol_price(symbol_upper, data, ttl=10)

                            # Update global snapshot
                            await self.update_global_snapshot(symbol_upper, data)

                        except Exception as e:
                            print(f"⚠️ Failed processing message ({self.symbol.upper()}): {e}")

            except Exception as e:
                print(f"⚠️ WS reconnecting ({self.symbol.upper()}) in 3s: {e}")
                await asyncio.sleep(3)

    async def update_global_snapshot(self, symbol: str, data: dict):
        """
        Updates the aggregated snapshot for dashboard.
        """
        snapshot_list = await get_crypto_prices() or []
        # Convert list to dict for easy update
        snapshot_dict = {item["symbol"]: item for item in snapshot_list if "symbol" in item}

        snapshot_dict[symbol] = {
            "symbol": symbol,
            "price": float(data.get("c", 0)),
            "change": data.get("P", "0%")
        }

        # Save back as list
        await set_crypto_prices(list(snapshot_dict.values()))


# =========================
# WS MANAGER
# =========================

class CryptoWebSocketManager:
    def __init__(self, symbols: List[str]):
        self.symbols = [s.lower() for s in symbols]

    async def start(self):
        tasks = [asyncio.create_task(SingleCryptoWebSocket(sym).run()) for sym in self.symbols]
        print(f"🚀 Binance WS started for {len(tasks)} cryptos (1 WS per crypto)")
        await asyncio.gather(*tasks)


# =========================
# DB LOADER
# =========================

def get_all_binance_symbols() -> List[str]:
    db = SessionLocal()
    try:
        symbols = db.query(Crypto.binance_symbol).all()
        return [s[0].lower() for s in symbols]
    finally:
        db.close()


# =========================
# STARTUP HELPER
# =========================

crypto_ws_manager: CryptoWebSocketManager | None = None

async def start_crypto_ws():
    global crypto_ws_manager

    symbols = get_all_binance_symbols()
    if not symbols:
        raise RuntimeError("❌ No crypto symbols found in DB")

    crypto_ws_manager = CryptoWebSocketManager(symbols)
    asyncio.create_task(crypto_ws_manager.start())