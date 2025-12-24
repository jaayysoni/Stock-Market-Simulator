from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, case
import os
import asyncio

# ----------------- DB / MODELS -----------------
from app.database.db import engine, Base, SessionLocal
from app.database.session import get_db
from app.models.crypto import Crypto
from app.models.transaction import Transaction

# ----------------- SERVICES / UTILS -----------------
from app.services.crypto_ws import start_crypto_ws
from app.utils.cache import get_crypto_prices
from app.utils.redis_client import get_redis, close_redis

# ----------------- APP INIT -----------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Crypto Trading Simulator",
    description="Simulate crypto trading with virtual money",
    version="1.0.0"
)

# ----------------- MIDDLEWARE -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- STATIC FILES -----------------
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# =================================================
#                  HTML PAGES
# =================================================

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(BASE_DIR, "static/dashboard.html"))

@app.get("/dashboard", include_in_schema=False)
def dashboard_page():
    return FileResponse(os.path.join(BASE_DIR, "static/dashboard.html"))

@app.get("/tradingterminal", include_in_schema=False)
def trading_terminal_page():
    return FileResponse(os.path.join(BASE_DIR, "static/tradingterminal.html"))

@app.get("/transactions", include_in_schema=False)
def transactions_page():
    return FileResponse(os.path.join(BASE_DIR, "static/transaction.html"))

@app.get("/portfolio", include_in_schema=False)
def portfolio_page():
    return FileResponse(os.path.join(BASE_DIR, "static/portfolio.html"))

# =================================================
#                 DASHBOARD API
# =================================================

@app.get("/dashboard/prices", tags=["Dashboard"])
async def get_dashboard_prices(
    db: Session = Depends(get_db)
) -> List[Dict]:
    """
    Returns list of cryptos with name, symbol, price, and 24h change
    """
    cryptos = db.query(Crypto).all()
    crypto_map = {c.binance_symbol: c for c in cryptos}

    data = await get_crypto_prices()
    if not data:
        return []

    response = []

    for item in data:
        symbol = item.get("binance_symbol") or item.get("symbol") or item.get("s")
        price = item.get("price") or item.get("p")

        if not symbol or price is None:
            continue

        crypto = crypto_map.get(symbol)
        name = crypto.name if crypto else symbol

        response.append({
            "name": name,
            "symbol": symbol,
            "price": float(price),
            "change": item.get("change", "0%")
        })

    return response

# =================================================
#                PORTFOLIO API
# =================================================

@app.get("/portfolio/holdings", tags=["Portfolio"])
async def get_portfolio_holdings():
    """
    Returns unsold crypto holdings for universal user (user_id=1)
    """
    db = SessionLocal()
    try:
        rows = db.query(
            Transaction.symbol,
            func.sum(
                case(
                    (Transaction.transaction_type == "BUY", Transaction.quantity),
                    else_=-Transaction.quantity
                )
            ).label("quantity")
        ).filter(
            Transaction.user_id == 1
        ).group_by(
            Transaction.symbol
        ).having(
            func.sum(
                case(
                    (Transaction.transaction_type == "BUY", Transaction.quantity),
                    else_=-Transaction.quantity
                )
            ) > 0
        ).all()

        if not rows:
            return {"holdings": []}

        prices_data = await get_crypto_prices() or []

        portfolio = []
        for r in rows:
            avg_price = db.query(
                func.sum(Transaction.quantity * Transaction.price)
                / func.sum(Transaction.quantity)
            ).filter(
                Transaction.user_id == 1,
                Transaction.symbol == r.symbol,
                Transaction.transaction_type == "BUY"
            ).scalar()

            live_price = next(
                (p["price"] for p in prices_data if p.get("binance_symbol") == r.symbol),
                None
            )

            profit_loss = (
                round((live_price - avg_price) * r.quantity, 2)
                if live_price is not None else None
            )

            portfolio.append({
                "symbol": r.symbol,
                "quantity": round(r.quantity, 8),
                "avg_price": round(avg_price, 2),
                "live_price": live_price,
                "profit_loss": profit_loss
            })

        return {"holdings": portfolio}
    finally:
        db.close()

# =================================================
#             TRANSACTION HISTORY API
# =================================================

@app.get("/api/transactions", tags=["Transactions"])
def get_all_transactions():
    db = SessionLocal()
    try:
        transactions = (
            db.query(Transaction)
            .order_by(Transaction.timestamp.desc())
            .all()
        )

        return [
            {
                "transaction_type": t.transaction_type.lower(),
                "crypto_symbol": t.crypto_symbol,
                "quantity": t.quantity,
                "price": t.price,
                "amount": None,               # frontend expects it
                "timestamp": t.timestamp,
                "status": "completed"
            }
            for t in transactions
        ]
    finally:
        db.close()

# =================================================
#              STARTUP / SHUTDOWN
# =================================================

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables ensured")

    for attempt in range(3):
        try:
            await get_redis()
            print("✅ Redis connected")
            break
        except Exception as e:
            print(f"⚠️ Redis attempt {attempt + 1} failed:", e)
            await asyncio.sleep(2)
    else:
        raise RuntimeError("❌ Redis is required")

    asyncio.create_task(start_crypto_ws())
    print("🚀 Binance WebSocket started")

@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Shutting down, closing Redis")
    await close_redis()