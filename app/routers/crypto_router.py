# app/routers/crypto_router.py

from fastapi import APIRouter
from app.services.price_service import get_all_crypto_prices

router = APIRouter(
    prefix="/crypto",
    tags=["Crypto"]
)

@router.get("/prices")
async def live_crypto_prices():
    """
    Get live prices of all cryptos.
    Returns cached data if available, otherwise fetches from WebSocket/cache service.
    """
    prices = await get_all_crypto_prices()
    return {"success": True, "data": prices}