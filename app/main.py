from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from collections import defaultdict, deque
import os
from fastapi import APIRouter
from app.models.balance import Balance
import asyncio

# ----------------- DB / MODELS -----------------
from app.database.db import engine, Base, SessionLocal
from app.database.session import get_db
from app.models.crypto import Crypto
from app.models.transaction import Transaction
from app.utils.cache import get_symbol_price

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
router = APIRouter()

@router.get("/portfolio/holdings", tags=["Portfolio"])
async def get_portfolio_holdings():
    """
    Returns unsold crypto holdings using FIFO (universal user)
    """
    db: Session = SessionLocal()
    try:
        # 1️⃣ Fetch all transactions ordered by time (no users)
        transactions = (
            db.query(Transaction)
            .order_by(Transaction.timestamp.asc(), Transaction.id.asc())
            .all()
        )

        # 2️⃣ FIFO processing per crypto
        portfolio_lots = defaultdict(deque)

        for tx in transactions:
            symbol = tx.crypto_symbol.upper()  # Ensure uppercase

            if tx.transaction_type == "BUY":
                portfolio_lots[symbol].append({
                    "quantity": tx.quantity,
                    "price": tx.price
                })

            elif tx.transaction_type == "SELL":
                qty_to_sell = tx.quantity
                while qty_to_sell > 0 and portfolio_lots[symbol]:
                    buy_lot = portfolio_lots[symbol][0]

                    if buy_lot["quantity"] <= qty_to_sell:
                        qty_to_sell -= buy_lot["quantity"]
                        portfolio_lots[symbol].popleft()
                    else:
                        buy_lot["quantity"] -= qty_to_sell
                        qty_to_sell = 0

        # 3️⃣ Build holdings with live prices
        holdings = []

        for symbol, lots in portfolio_lots.items():
            total_qty = sum(lot["quantity"] for lot in lots)
            if total_qty <= 0:
                continue

            avg_price = sum(
                lot["quantity"] * lot["price"] for lot in lots
            ) / total_qty

            # 🔥 Query live price from Redis WS cache using symbol + 'USDT'
            symbol_usdt = f"{symbol}USDT"
            price_data = await get_symbol_price(symbol_usdt)
            live_price = None
            if price_data:
                live_price = float(
                    price_data.get("c") or
                    price_data.get("p") or
                    price_data.get("price", 0)
                )

            holdings.append({
                "symbol": symbol,
                "quantity": round(total_qty, 8),
                "avg_price": round(avg_price, 2),
                "live_price": live_price,
                "profit_loss": (
                    round((live_price - avg_price) * total_qty, 2)
                    if live_price is not None else 0
                )
            })

        return {"holdings": holdings}

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


app.include_router(router, prefix="/api")

balance_router = APIRouter()



@balance_router.get("/balance", tags=["Balance"])
def get_balance(db: Session = Depends(get_db)):
    balance = db.query(Balance).first()

    if not balance:
        balance = Balance(amount=100000.0)
        db.add(balance)
        db.commit()
        db.refresh(balance)

    return {"balance": round(balance.amount, 2)}


@balance_router.post("/balance/update", tags=["Balance"])
def update_balance(payload: dict, db: Session = Depends(get_db)):
    """
    Update virtual balance by adding or removing funds.
    Payload: { "action": "add" | "remove", "amount": float }
    """
    action = payload.get("action")
    try:
        amount = float(payload.get("amount", 0))
    except (TypeError, ValueError):
        return JSONResponse(
            status_code=400,
            content={"error": "Amount must be a number"}
        )

    if amount <= 0:
        return JSONResponse(
            status_code=400,
            content={"error": "Amount must be positive"}
        )

    # Ensure balance exists
    balance = db.query(Balance).first()
    if not balance:
        balance = Balance(amount=100000.0)
        db.add(balance)
        db.commit()
        db.refresh(balance)

    if action == "add":
        balance.amount += amount
    elif action == "remove":
        if balance.amount < amount:
            return JSONResponse(
                status_code=400,
                content={"error": "Insufficient balance"}
            )
        balance.amount -= amount
    else:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid action, must be 'add' or 'remove'"}
        )

    db.commit()
    db.refresh(balance)

    return {"balance": round(balance.amount, 2)}

app.include_router(balance_router, prefix="/api")


# =================================================
#              ORDER (BUY / SELL) API
# =================================================
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from app.database.session import get_db
from app.models.transaction import Transaction
from app.models.balance import Balance
from app.utils.cache import get_symbol_price

order_router = APIRouter()


# ----------------------------
# Pydantic Model
# ----------------------------
class OrderRequest(BaseModel):
    symbol: str
    quantity: float


# ----------------------------
# BUY CRYPTO
# ----------------------------
@order_router.post("/order/buy", tags=["Order"])
async def buy_crypto(order: OrderRequest, db: Session = Depends(get_db)):
    symbol = order.symbol.upper()
    quantity = order.quantity

    if not symbol or quantity <= 0:
        return JSONResponse(status_code=400, content={"error": "Invalid buy request"})

    # 1️⃣ Get live price from Redis WS cache
    price_data = await get_symbol_price(symbol)
    if not price_data:
        return JSONResponse(status_code=400, content={"error": "Live price not available"})

    price = float(price_data.get("c") or price_data.get("p") or price_data.get("price", 0))
    total_cost = price * quantity

    # 2️⃣ Ensure balance exists
    balance = db.query(Balance).first()
    if not balance:
        balance = Balance(amount=100000.0)
        db.add(balance)
        db.commit()
        db.refresh(balance)

    # 3️⃣ Balance check
    if balance.amount < total_cost:
        return JSONResponse(
            status_code=400,
            content={
                "error": "Insufficient balance",
                "required": round(total_cost, 2),
                "available": round(balance.amount, 2)
            }
        )

    # 4️⃣ Deduct balance
    balance.amount -= total_cost

    # 5️⃣ Insert BUY transaction
    tx = Transaction(
        transaction_type="BUY",
        crypto_symbol=symbol.replace("USDT", ""),
        quantity=quantity,
        price=price
    )
    db.add(tx)
    db.commit()

    return {
        "message": "Order executed",
        "side": "BUY",
        "symbol": symbol,
        "quantity": round(quantity, 8),
        "price": round(price, 2),
        "spent": round(total_cost, 2),
        "balance": round(balance.amount, 2)
    }


# ----------------------------
# SELL CRYPTO
# ----------------------------
@order_router.post("/order/sell", tags=["Order"])
async def sell_crypto(order: OrderRequest, db: Session = Depends(get_db)):
    symbol = order.symbol.upper()
    quantity = order.quantity

    if not symbol or quantity <= 0:
        return JSONResponse(status_code=400, content={"error": "Invalid sell request"})

    base_symbol = symbol.replace("USDT", "")

    # 1️⃣ Calculate available quantity
    bought_qty = (
        db.query(func.coalesce(func.sum(Transaction.quantity), 0))
        .filter(Transaction.crypto_symbol == base_symbol, Transaction.transaction_type == "BUY")
        .scalar()
    )

    sold_qty = (
        db.query(func.coalesce(func.sum(Transaction.quantity), 0))
        .filter(Transaction.crypto_symbol == base_symbol, Transaction.transaction_type == "SELL")
        .scalar()
    )

    available_qty = bought_qty - sold_qty

    if available_qty < quantity:
        return JSONResponse(
            status_code=400,
            content={"error": "Not enough holdings", "available": round(available_qty, 8)}
        )

    # 2️⃣ Get live price
    price_data = await get_symbol_price(symbol)
    if not price_data:
        return JSONResponse(status_code=400, content={"error": "Live price not available"})

    price = float(price_data.get("c") or price_data.get("p") or price_data.get("price", 0))
    total_credit = price * quantity

    # 3️⃣ Credit balance
    balance = db.query(Balance).first()
    if not balance:
        balance = Balance(amount=100000.0)
        db.add(balance)
        db.commit()
        db.refresh(balance)

    balance.amount += total_credit

    # 4️⃣ Insert SELL transaction
    tx = Transaction(
        transaction_type="SELL",
        crypto_symbol=base_symbol,
        quantity=quantity,
        price=price
    )
    db.add(tx)
    db.commit()

    return {
        "message": "Order executed",
        "side": "SELL",
        "symbol": symbol,
        "quantity": round(quantity, 8),
        "price": round(price, 2),
        "received": round(total_credit, 2),
        "balance": round(balance.amount, 2)
    }


# ----------------------------
# Include router in main app
# ----------------------------
app.include_router(order_router, prefix="/api")