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
# COMBINED CRYPTO WS
# =========================

class CombinedCryptoWebSocket:
    def __init__(self, symbols: List[str]):
        self.symbols = [s.lower() for s in symbols]
        self.ws_url = settings.BINANCE_WS_URL  # e.g., "wss://stream.binance.com:9443"

    def _build_stream_url(self) -> str:
        """
        Binance combined stream URL for multiple symbols.
        """
        stream_names = [f"{s}@ticker" for s in self.symbols]
        streams = "/".join(stream_names)
        return f"{self.ws_url}/stream?streams={streams}"

    async def run(self):
        url = self._build_stream_url()
        print(f"🚀 WS connecting to combined stream ({len(self.symbols)} symbols)")

        while True:
            try:
                async with websockets.connect(url, ping_interval=20, ping_timeout=20) as ws:
                    print(f"✅ WS connected to combined stream ({len(self.symbols)} symbols)")
                    async for msg in ws:
                        try:
                            data = json.loads(msg)
                            # Binance combined stream wraps data in "data" key
                            payload = data.get("data")
                            if not payload or "s" not in payload:
                                continue

                            symbol_upper = payload["s"].upper()

                            # Cache per-symbol
                            await set_symbol_price(symbol_upper, payload, ttl=10)

                            # Update global snapshot
                            await self.update_global_snapshot(symbol_upper, payload)

                        except Exception as e:
                            print(f"⚠️ Failed processing message: {e}")

            except Exception as e:
                print(f"⚠️ WS reconnecting combined stream in 3s: {e}")
                await asyncio.sleep(3)

    async def update_global_snapshot(self, symbol: str, data: dict):
        """
        Updates the aggregated snapshot for dashboard.
        """
        snapshot_list = await get_crypto_prices() or []
        snapshot_dict = {item["symbol"]: item for item in snapshot_list if "symbol" in item}

        snapshot_dict[symbol] = {
            "symbol": symbol,
            "price": float(data.get("c", 0)),
            "change": data.get("P", "0%")
        }

        await set_crypto_prices(list(snapshot_dict.values()))

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

crypto_ws_manager: CombinedCryptoWebSocket | None = None

async def start_crypto_ws():
    global crypto_ws_manager

    symbols = get_all_binance_symbols()
    if not symbols:
        raise RuntimeError("❌ No crypto symbols found in DB")

    crypto_ws_manager = CombinedCryptoWebSocket(symbols)
    asyncio.create_task(crypto_ws_manager.run())