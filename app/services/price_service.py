# app/services/price_service.py

import json
from typing import List

from app.database.db import SessionLocal
from app.models.crypto import Crypto
from app.utils.cache import get_symbol_price

# ==============================
# Live crypto prices (current day only)
# ==============================
async def get_all_crypto_prices() -> List[dict]:
    """
    Returns live prices for all supported cryptos.
    Fetches prices directly from Redis (updated by WebSocket service).
    """
    result: List[dict] = []

    with SessionLocal() as db:
        cryptos = db.query(Crypto).all()
        if not cryptos:
            return result

        for crypto in cryptos:
            data = await get_symbol_price(crypto.binance_symbol)
            price = 0.0
            change_pct = "0%"
            market_cap = 0.0

            if data:
                try:
                    price = float(data.get("c", 0))
                    change_pct = data.get("P", "0%")
                    market_cap = float(data.get("market_cap", 0)) or \
                                 price * getattr(crypto, "circulating_supply", 0)
                except (ValueError, TypeError):
                    price = getattr(crypto, "last_known_price", 0)
                    market_cap = price * getattr(crypto, "circulating_supply", 0)
            else:
                # Redis key missing (WS not ready yet)
                price = getattr(crypto, "last_known_price", 0)
                market_cap = price * getattr(crypto, "circulating_supply", 0)

            result.append({
                "name": crypto.name,
                "symbol": crypto.universal_symbol,
                "binance_symbol": crypto.binance_symbol,
                "price": price,
                "change": change_pct,
                "market_cap": market_cap
            })

    return result