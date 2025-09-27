# app/routers/stock_router.py

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket,WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.database.session import get_user_db
from app.models.stock import Stock
from app.services.stock_service import get_multiple_stock_prices, load_nse_top_500
import time
from redis.asyncio import Redis

router = APIRouter(
    tags=["Stocks"]
)

# ==============================
# Cache for Top 500 prices + indices
# ==============================
CACHE_TTL = 300  # 5 minutes
_top500_cache = {"data": {}, "timestamp": 0}


# ==============================
# Get Market Indices (BSE, NSE, BankNifty)
# ==============================
@router.get("/indices")
def market_indices(exchange: str = Query("NSE")):
    prices = get_cached_top500_prices(exchange)
    # Make sure keys exactly match the frontend expectation
    return {
        "BSE": prices.get("BSE", {"price": 0, "change": 0}),
        "NSE": prices.get("NSE", {"price": 0, "change": 0}),
        "BankNifty": prices.get("BANKNIFTY", {"price": 0, "change": 0})
    }

def get_cached_top500_prices(exchange: str = "NSE") -> Dict[str, Dict[str, Optional[float]]]:
    """
    Returns cached Top 500 prices with indices if cache is still valid.
    Otherwise, fetch fresh prices and update cache.
    """
    current_time = time.time()
    if current_time - _top500_cache["timestamp"] > CACHE_TTL or not _top500_cache["data"]:
        symbols = load_nse_top_500()
        if not symbols:
            raise HTTPException(status_code=404, detail="Top 500 symbols not found")
        # Add indices for market overview
        symbols += ["BSE", "NSE", "BANKNIFTY"]
        try:
            prices = get_multiple_stock_prices(symbols, exchange)
            _top500_cache["data"] = prices
            _top500_cache["timestamp"] = current_time
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch Top 500 prices: {e}")
    return _top500_cache["data"]

# ==============================
# Get Stock by ID from DB
# ==============================
@router.get("/{stock_id}")
def get_stock(stock_id: int, db: Session = Depends(get_user_db)):
    """
    Fetch stock details from the database by ID.
    """
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

# ==============================
# Get live prices for multiple stocks
# ==============================
@router.get("/prices", response_model=Dict[str, Dict[str, Optional[float]]])
def list_stock_prices(
    symbols: str = Query("RELIANCE,TCS,INFY"),
    exchange: str = Query("NSE")
):
    """
    Get current prices of multiple NSE/BSE stocks.
    Query parameter `symbols` should be comma-separated.
    Example: /stocks/prices?symbols=RELIANCE,TCS
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    try:
        prices = get_multiple_stock_prices(symbol_list, exchange)
        return {"prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch prices: {e}")

# ==============================
# Get all NSE Top 500 symbols
# ==============================
@router.get("/all", response_model=List[str])
def all_stocks():
    symbols = load_nse_top_500()
    if not symbols:
        raise HTTPException(status_code=404, detail="Top 500 symbols not found")
    return symbols
# ==============================
# Get live prices for Top 500 NSE stocks + indices
# ==============================
@router.get("/top500", response_model=Dict[str, Dict[str, Optional[float]]])
def top_500_prices(exchange: str = Query("NSE")):
    """
    Fetch live prices for NSE Top 500 stocks with caching (5-min TTL),
    including BSE, NSE, and BANKNIFTY indices.
    """
    try:
        prices = get_cached_top500_prices(exchange)
        return {"prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


# Redis client (same DB as price_updater)

redis = Redis(host="localhost", port=6379, db=0, decode_responses=True)

@router.websocket("/ws/stocks")
async def websocket_stocks(ws: WebSocket):
    await ws.accept()
    print("✅ WebSocket client connected:", ws.client)

    try:
        pubsub = redis.pubsub()
        await pubsub.subscribe("stocks:updates")

        async for message in pubsub.listen():
            if message["type"] == "message":
                try:
                    await ws.send_text(message["data"])
                except:
                    break
    except WebSocketDisconnect:
        print("❌ WebSocket client disconnected:", ws.client)
    finally:
        await pubsub.unsubscribe("stocks:updates")