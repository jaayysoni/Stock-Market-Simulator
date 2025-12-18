# app/routers/crypto_router.py
from fastapi import APIRouter, Query
from typing import List
from app.services.price_service import get_all_crypto_prices, get_crypto_history

router = APIRouter(tags=["Crypto"])

# ==============================
# Live crypto prices endpoint
# ==============================
@router.get("/prices")
async def live_crypto_prices(
    limit: int = Query(90, ge=1, le=100, description="Number of top cryptos to return")
):
    """
    Get live prices of top cryptos.
    Returns cached data from Redis if available.
    """
    prices: List[dict] = await get_all_crypto_prices() or []

    # Sort by market cap if available, otherwise by price
    prices_sorted = sorted(
        prices,
        key=lambda x: float(x.get("market_cap", x.get("price", 0))),
        reverse=True
    )

    return {"success": True, "data": prices_sorted[:limit]}


# ==============================
# Historical price endpoint
# ==============================
@router.get("/history")
async def crypto_history(
    symbol: str = Query(..., description="Crypto symbol like BTCUSDT"),
    time_range: str = Query("1M", description="Range: 1D,7D,1M,3M,6M,1Y,3Y,5Y,ALL")
):
    """
    Return historical OHLC/candle data for a crypto.
    Uses Redis cache first, falls back to mock data if needed.
    """
    normalized_symbol = symbol.upper()
    
    # Fetch historical candles from service (handles caching/fallback)
    candles = await get_crypto_history(normalized_symbol, time_range)
    
    # Ensure response always has "time" in ms and "close" as float
    formatted_candles = [
        {
            "time": int(candle["time"]),  # milliseconds
            "close": float(candle["close"])
        } for candle in candles
    ] if candles else []

    return {
        "success": True,
        "symbol": normalized_symbol,
        "range": time_range,
        "candles": formatted_candles
    }