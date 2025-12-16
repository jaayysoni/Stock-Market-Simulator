from fastapi import APIRouter, Depends
from typing import List, Dict
from app.utils.cache import get_cached_data
from app.models.crypto import Crypto
from app.database.db import SessionLocal

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/prices")
async def get_prices() -> List[Dict]:
    """
    Returns latest prices for all cryptos from Redis cache.
    """
    db = SessionLocal()
    try:
        symbols = db.query(Crypto.binance_symbol).all()
        result = []
        for s in symbols:
            key = f"crypto:{s[0].lower()}"
            data = await get_cached_data(key)
            if data:
                result.append({
                    "symbol": s[0],
                    "price": float(data['c'])  # current price from WS
                })
        return result
    finally:
        db.close()