# app/routers/stock_router.py

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Set
from app.database.session import get_user_db
from app.models.stock import Stock
from app.services.stock_service import get_multiple_stock_prices, load_nse_top_500  # Finnhub for equities
from app.services.yfinance_client import get_index_price  # yfinance for indices
from app.services.finnhub_client import finnhub_client
from app.utils.cache import get_redis
import time
import asyncio
import json
from redis.asyncio import Redis

router = APIRouter(tags=["Stocks"])

# ==============================
# Cache for Top 500 (Finnhub)
# ==============================
CACHE_TTL = 300  # 5 minutes
_top500_cache = {"data": {}, "timestamp": 0}

# ==============================
# Redis client
# ==============================
redis: Redis = None

@router.on_event("startup")
async def setup_redis():
    global redis
    redis = await get_redis()


# ==============================
# Get Market Indices (yfinance only)
# ==============================
@router.get("/indices")
def market_indices():
    """
    Fetch indices only from yfinance (BSE, NSE, BankNifty).
    """
    try:
        return {
            "BSE": get_index_price("^BSESN"),         # BSE Sensex
            "NSE": get_index_price("^NSEI"),          # NSE Nifty 50
            "BankNifty": get_index_price("^NSEBANK")  # Nifty Bank
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch indices: {e}")


# ==============================
# Internal helper - cache Top 500 (Finnhub only)
# ==============================
def get_cached_top500_prices(exchange: str = "NSE") -> Dict[str, Dict[str, Optional[float]]]:
    """
    Returns cached Top 500 stock prices (via Finnhub).
    Does NOT include indices.
    """
    current_time = time.time()
    if current_time - _top500_cache["timestamp"] > CACHE_TTL or not _top500_cache["data"]:
        symbols = load_nse_top_500()
        if not symbols:
            raise HTTPException(status_code=404, detail="Top 500 symbols not found")
        try:
            prices = get_multiple_stock_prices(symbols, exchange)  # Finnhub
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
# Get live prices for multiple stocks (Finnhub only)
# ==============================
@router.get("/prices", response_model=Dict[str, Dict[str, Optional[float]]])
def list_stock_prices(
    symbols: str = Query("RELIANCE,TCS,INFY"),
    exchange: str = Query("NSE")
):
    """
    Get current stock prices (equities) from Finnhub.
    Query parameter `symbols` should be comma-separated.
    Example: /stocks/prices?symbols=RELIANCE,TCS
    """
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    try:
        prices = get_multiple_stock_prices(symbol_list, exchange)  # Finnhub
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
# Get live prices for Top 500 (Finnhub only)
# ==============================
@router.get("/top500", response_model=Dict[str, Dict[str, Optional[float]]])
def top_500_prices(exchange: str = Query("NSE")):
    """
    Fetch live prices for NSE Top 500 stocks via Finnhub (with 5-min cache).
    """
    try:
        prices = get_cached_top500_prices(exchange)
        return {"prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==============================
# WebSocket (per-client subscriptions via Redis pubsub)
# ==============================
@router.websocket("/ws/stocks")
async def websocket_stocks(ws: WebSocket):
    """
    WebSocket endpoint for clients to receive live updates.
    Each client only receives updates for the stocks it subscribes to.
    """
    await ws.accept()
    client_symbols: Set[str] = set()  # Track symbols this client is viewing
    pubsub = redis.pubsub()
    await pubsub.subscribe("stocks:updates")

    async def send_updates():
        async for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                symbol = data.get("symbol")
                if symbol in client_symbols:
                    await ws.send_text(json.dumps(data))

    send_task = asyncio.create_task(send_updates())

    try:
        while True:
            # Receive subscription messages from client
            msg = await ws.receive_text()
            msg_data = json.loads(msg)
            action = msg_data.get("action")
            symbol = msg_data.get("symbol")

            if not symbol:
                continue

            if action == "subscribe":
                client_symbols.add(symbol)
                await finnhub_client.subscribe(symbol)
            elif action == "unsubscribe":
                client_symbols.discard(symbol)
                await finnhub_client.unsubscribe(symbol)

    except WebSocketDisconnect:
        print(f"❌ WebSocket client disconnected: {ws.client}")
    finally:
        send_task.cancel()
        for symbol in client_symbols:
            await finnhub_client.unsubscribe(symbol)
        await pubsub.unsubscribe("stocks:updates")