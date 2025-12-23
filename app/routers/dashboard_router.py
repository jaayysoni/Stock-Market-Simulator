from fastapi import APIRouter,Depends
from typing import List, Dict
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.crypto import Crypto
from app.utils.cache import get_crypto_prices

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/prices")
async def get_prices(db: Session = Depends(get_db)) -> List[Dict]:
    """
    Returns list of cryptos with name, symbol, price, and 24h change
    """
    # 1️⃣ Fetch crypto master data from DB
    cryptos = db.query(Crypto).all()
    crypto_map = {c.binance_symbol: c for c in cryptos}  # map for fast lookup

    # 2️⃣ Get live prices (cached)
    data = await get_crypto_prices()
    if not data:
        return []

    response = []

    for item in data:
        # Accept all possible WS/REST formats
        symbol = item.get("binance_symbol") or item.get("symbol") or item.get("s")
        price = item.get("price") or item.get("p")

        if not symbol or price is None:
            continue

        crypto = crypto_map.get(symbol)
        name = crypto.name if crypto else symbol  # use DB name if exists

        response.append({
            "name": name,                 # ✅ proper crypto name
            "symbol": symbol,             # Binance symbol (for trade)
            "price": float(price),
            "change": item.get("change", "0%")
        })

    return response