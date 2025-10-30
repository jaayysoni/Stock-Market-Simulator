# app/routers/stock_router.py

import time
import asyncio
import json
import logging
import yfinance as yf
from typing import List, Dict, Optional, Set

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from redis.asyncio import Redis

from app.database.db import get_user_db
from app.models.stock import Stock
from app.services.stock_service import get_multiple_stock_prices, load_nse_top_500
from app.services.finnhub_client import finnhub_client
from app.utils.cache import get_redis
from app.tasks.nifty_tasks import get_cached_nifty_history, get_cached_nifty_latest


# ===================================================
# Router & Logging Setup
# ===================================================
router = APIRouter(tags=["Stocks"])
logger = logging.getLogger("stock_router")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ===================================================
# Cache & Redis Setup
# ===================================================
CACHE_TTL = 900  # 15 minutes for Top 500 cache
_top500_cache = {"data": {}, "timestamp": 0}
redis: Optional[Redis] = None


@router.on_event("startup")
async def setup_redis():
    """Initialize Redis connection at startup."""
    global redis
    try:
        redis = await get_redis()
        logger.info("✅ Redis client initialized successfully for Stock Router.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Redis client: {e}")


# ===================================================
# Market Indices (with Redis caching)
# ===================================================
@router.get("/indices")
async def market_indices():
    """
    Return major indices: BSE, NSE, BankNifty, Nifty50.
    Cached in Redis for 60 seconds.
    """
    redis_client = await get_redis()
    CACHE_KEY = "market_indices"
    CACHE_TTL = 60  # 1 minute

    try:
        key_type = await redis_client.type(CACHE_KEY)
        if key_type and key_type != b"string":
            await redis_client.delete(CACHE_KEY)

        cached = await redis_client.get(CACHE_KEY)
        if cached:
            logger.info("✅ Served indices from Redis cache.")
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"⚠️ Redis cache fetch failed: {e}")

    result = {}
    symbols = {"BSE": "^BSESN", "NSE": "^NSEI", "BankNifty": "^NSEBANK"}

    for name, symbol in symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty and len(hist["Close"]) >= 2:
                latest_price = float(hist["Close"].iloc[-1])
                previous_price = float(hist["Close"].iloc[-2])
                change_percent = ((latest_price - previous_price) / previous_price) * 100
                result[name] = {
                    "price": round(latest_price, 2),
                    "change": round(change_percent, 2)
                }
            else:
                result[name] = {"price": 0, "change": 0}
        except Exception as e:
            logger.error(f"Error fetching {name} data: {e}")
            result[name] = {"price": 0, "change": 0}

    try:
        nifty = await get_cached_nifty_latest()
        result["Nifty50"] = nifty
    except Exception as e:
        logger.warning(f"Nifty50 background data unavailable: {e}")
        result["Nifty50"] = {"price": 0, "change": 0}

    try:
        await redis_client.set(CACHE_KEY, json.dumps(result), ex=CACHE_TTL)
        logger.info("🧠 Updated Redis cache for /indices route.")
    except Exception as e:
        logger.warning(f"⚠️ Redis cache set failed: {e}")

    return result


# ===================================================
# Top 500 (Finnhub Cached)
# ===================================================
def get_cached_top500_prices(exchange: str = "NSE") -> Dict[str, Dict[str, Optional[float]]]:
    """Return cached Top 500 prices with a 15-minute TTL."""
    current_time = time.time()
    if current_time - _top500_cache["timestamp"] > CACHE_TTL or not _top500_cache["data"]:
        symbols = load_nse_top_500()
        if not symbols:
            raise HTTPException(status_code=404, detail="Top 500 symbols not found")
        try:
            prices = get_multiple_stock_prices(symbols, exchange)
            _top500_cache["data"] = prices
            _top500_cache["timestamp"] = current_time
            logger.info("🧠 Refreshed Top 500 stock cache.")
        except Exception as e:
            logger.error(f"Failed to fetch Top 500 prices: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch Top 500 prices: {e}")
    else:
        logger.info("✅ Served Top 500 prices from in-memory cache.")
    return _top500_cache["data"]


# ===================================================
# Stock by ID
# ===================================================
@router.get("/{stock_id}")
def get_stock(stock_id: int, db: Session = Depends(get_user_db)):
    """Fetch a stock by ID from DB."""
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        logger.warning(f"Stock ID {stock_id} not found.")
        raise HTTPException(status_code=404, detail="Stock not found")
    logger.info(f"Fetched stock ID {stock_id} successfully.")
    return stock


# ===================================================
# Prices for Multiple Stocks (Finnhub)
# ===================================================
@router.get("/prices", response_model=Dict[str, Dict[str, Optional[float]]])
def list_stock_prices(
    symbols: str = Query("RELIANCE,TCS,INFY"),
    exchange: str = Query("NSE")
):
    """Fetch live prices for multiple given symbols."""
    symbol_list = [s.strip().upper() for s in symbols.split(",")]
    try:
        prices = get_multiple_stock_prices(symbol_list, exchange)
        logger.info(f"Fetched prices for {len(symbol_list)} symbols from Finnhub.")
        return {"prices": prices}
    except Exception as e:
        logger.error(f"Failed to fetch prices: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch prices: {e}")


# ===================================================
# All NSE Top 500 Symbols
# ===================================================
@router.get("/all", response_model=List[str])
def all_stocks():
    """Return list of all Top 500 NSE symbols."""
    symbols = load_nse_top_500()
    if not symbols:
        logger.error("Top 500 symbols not found.")
        raise HTTPException(status_code=404, detail="Top 500 symbols not found")
    logger.info(f"✅ Loaded {len(symbols)} NSE symbols successfully.")
    return symbols


# ===================================================
# Top 500 Prices (Finnhub)
# ===================================================
@router.get("/top500", response_model=Dict[str, Dict[str, Optional[float]]])
def top_500_prices(exchange: str = Query("NSE")):
    """Return cached Top 500 stock prices."""
    try:
        prices = get_cached_top500_prices(exchange)
        return {"prices": prices}
    except Exception as e:
        logger.error(f"Failed to serve Top 500 prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===================================================
# WebSocket for Real-time Stocks
# ===================================================
@router.websocket("/ws/stocks")
async def websocket_stocks(ws: WebSocket):
    """Real-time WebSocket updates for subscribed stocks."""
    await ws.accept()
    client_symbols: Set[str] = set()
    pubsub = redis.pubsub()
    await pubsub.subscribe("stocks:updates")

    logger.info(f"🔌 New WebSocket connection: {ws.client}")

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

            if action == "subscribe" and symbol not in client_symbols:
                client_symbols.add(symbol)
                await finnhub_client.subscribe(symbol)
                logger.info(f"📈 Subscribed to {symbol} via WebSocket.")

            elif action == "unsubscribe" and symbol in client_symbols:
                client_symbols.discard(symbol)
                await finnhub_client.unsubscribe(symbol)
                logger.info(f"📉 Unsubscribed from {symbol} via WebSocket.")

    except WebSocketDisconnect:
        logger.warning(f"❌ WebSocket client disconnected: {ws.client}")
    finally:
        send_task.cancel()
        for symbol in client_symbols:
            await finnhub_client.unsubscribe(symbol)
        await pubsub.unsubscribe("stocks:updates")
        logger.info(f"🧹 Cleaned up subscriptions for client {ws.client}.")


# ===================================================
# Nifty50 History
# ===================================================
@router.get("/nifty50/history")
async def nifty50_history(days: int = 30):
    """Return Nifty50 historical data from Redis cache."""
    logger.info(f"Fetching Nifty50 history for {days} days.")
    return await get_cached_nifty_history(days)