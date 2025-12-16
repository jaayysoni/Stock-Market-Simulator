# app/routers/crypto_router.py
from fastapi import APIRouter, Query
from typing import List
from app.services.price_service import get_all_crypto_prices

router = APIRouter(tags=["Crypto"])

@router.get("/prices")
async def live_crypto_prices(
    limit: int = Query(90, ge=1, le=100, description="Number of top cryptos to return")
):
    """
    Get live prices of top cryptos.

    Returns cached data from Redis/WebSocket service if available.

    Query param:
    - limit: Number of top cryptos to return (default 90)
    """
    # Fetch all crypto prices from Redis
    prices: List[dict] = await get_all_crypto_prices() or []

    # Sort by market cap if available, otherwise fallback to price
    prices_sorted = sorted(
        prices,
        key=lambda x: float(x.get("market_cap", x.get("price", 0))),
        reverse=True
    )

    # Limit to the requested number
    limited_prices = prices_sorted[:limit]

    return {"success": True, "data": limited_prices}