# app/routers/stock_router.py

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Set
from app.database.session import get_user_db
from app.models.stock import Stock
from app.services.stock_service import get_multiple_stock_prices, load_nse_top_500  # Finnhub for equities
from app.services.finnhub_client import finnhub_client
from app.utils.cache import get_redis
from app.tasks.nifty_tasks import get_cached_nifty_history, get_cached_nifty_latest

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
# Market Indices (with Redis caching)
# ==============================
@router.get("/indices")
async def market_indices():
    """
    Return major indices: BSE, NSE, BankNifty, Nifty50.
    Nifty50 is fetched from our background Redis cache.
    """
    redis_client = await get_redis()
    CACHE_KEY = "market_indices"
    CACHE_TTL = 60  # cache 1 min

    cached = await redis_client.get(CACHE_KEY)
    if cached:
        return json.loads(cached)

    result = {}

    # BSE, NSE, BankNifty using yfinance (or keep your previous live method)
    import yfinance as yf
    symbols = {"BSE": "^BSESN", "NSE": "^NSEI", "BankNifty": "^NSEBANK"}
    for name, symbol in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist['Close']) >= 2:
                latest_price = float(hist['Close'].iloc[-1])
                previous_price = float(hist['Close'].iloc[-2])
                change_percent = ((latest_price - previous_price) / previous_price) * 100
                result[name] = {"price": round(latest_price,2), "change": round(change_percent,2)}
            else:
                result[name] = {"price": 0, "change": 0}
        except Exception:
            result[name] = {"price": 0, "change": 0}

    # Nifty50 from Redis cache
    try:
        nifty = await get_cached_nifty_latest()
        result["Nifty50"] = nifty
    except Exception:
        result["Nifty50"] = {"price": 0, "change": 0}

    await redis_client.set(CACHE_KEY, json.dumps(result), ex=CACHE_TTL)
    return result

# ==============================
# Helper - Top 500 cache (Finnhub)
# ==============================
def get_cached_top500_prices(exchange: str = "NSE") -> Dict[str, Dict[str, Optional[float]]]:
    current_time = time.time()
    if current_time - _top500_cache["timestamp"] > CACHE_TTL or not _top500_cache["data"]:
        symbols = load_nse_top_500()
        if not symbols:
            raise HTTPException(status_code=404, detail="Top 500 symbols not found")
        try:
            prices = get_multiple_stock_prices(symbols, exchange)
            _top500_cache["data"] = prices
            _top500_cache["timestamp"] = current_time
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch Top 500 prices: {e}")
    return _top500_cache["data"]

# ==============================
# Stock by ID
# ==============================
@router.get("/{stock_id}")
def get_stock(stock_id: int, db: Session = Depends(get_user_db)):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

# ==============================
# Prices for multiple stocks (Finnhub)
# ==============================
@router.get("/prices", response_model=Dict[str, Dict[str, Optional[float]]])
def list_stock_prices(symbols: str = Query("RELIANCE,TCS,INFY"), exchange: str = Query("NSE")):
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    try:
        prices = get_multiple_stock_prices(symbol_list, exchange)
        return {"prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch prices: {e}")

# ==============================
# All NSE Top 500 symbols
# ==============================
@router.get("/all", response_model=List[str])
def all_stocks():
    symbols = load_nse_top_500()
    if not symbols:
        raise HTTPException(status_code=404, detail="Top 500 symbols not found")
    return symbols

# ==============================
# Top 500 prices (Finnhub)
# ==============================
@router.get("/top500", response_model=Dict[str, Dict[str, Optional[float]]])
def top_500_prices(exchange: str = Query("NSE")):
    try:
        prices = get_cached_top500_prices(exchange)
        return {"prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================
# WebSocket
# ==============================
@router.websocket("/ws/stocks")
async def websocket_stocks(ws: WebSocket):
    await ws.accept()
    client_symbols: Set[str] = set()
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

# ==============================
# Nifty50 history
# ==============================
@router.get("/nifty50/history")
async def nifty50_history(days: int = 30):
    """
    Return Nifty 50 historical data from Redis cache.
    """
    return await get_cached_nifty_history(days)