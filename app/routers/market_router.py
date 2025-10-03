from fastapi import APIRouter
import json
from app.utils.cache import get_redis

router = APIRouter()

@router.get("/indices")
async def get_market_indices():
    redis_client = await get_redis()
    data = await redis_client.hgetall("market_indices")
    
    # Convert string values to float
    for key in data:
        try:
            data[key] = float(data[key])
        except (TypeError, ValueError):
            data[key] = None
    return {
        "BSE": {"price": data.get("BSE_price"), "change": data.get("BSE_change")},
        "NSE": {"price": data.get("NSE_price"), "change": data.get("NSE_change")},
        "BankNifty": {"price": data.get("BankNifty_price"), "change": data.get("BankNifty_change")},
    }

@router.get("/top-movers")
async def get_top_movers():
    redis_client = await get_redis()
    gainers_raw = await redis_client.get("top_gainers") or "[]"
    losers_raw = await redis_client.get("top_losers") or "[]"
    
    gainers = json.loads(gainers_raw)
    losers = json.loads(losers_raw)
    
    return {
        "gainers": gainers,
        "losers": losers
    }