from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
import asyncio

from app.database.db import engine, Base
from app.models import transaction, crypto
from app.routers import dashboard_router, portfolio_router, terminal_router, transaction_router
from app.services.crypto_ws import start_crypto_ws
from app.utils.redis_client import get_redis, close_redis

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Crypto Trading Simulator",
    description="Simulate crypto trading with virtual money, view transactions, and more.",
    version="1.0.0"
)

# ----------------- Middleware -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Static Files -----------------
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ----------------- Routers -----------------
app.include_router(dashboard_router.router)
app.include_router(portfolio_router.router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(terminal_router.router, tags=["Trading Terminal"])
app.include_router(transaction_router.router, prefix="/transactions", tags=["Transactions"])

# ----------------- Pages -----------------
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(BASE_DIR, "static/dashboard.html"))

@app.get("/dashboard", include_in_schema=False, response_class=HTMLResponse)
def dashboard_page():
    path = os.path.join(BASE_DIR, "static/dashboard.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/tradingterminal", include_in_schema=False)
def trading_terminal_page():
    return FileResponse(os.path.join(BASE_DIR, "static/tradingterminal.html"))

@app.get("/transactions", include_in_schema=False)
def transactions_page():
    return FileResponse(os.path.join(BASE_DIR, "static/transaction.html"))

# ----------------- Startup Event -----------------
@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ensured")
    except Exception as e:
        print("❌ Error creating database tables:", e)

    # Initialize Redis
    for attempt in range(3):
        try:
            await get_redis()
            print("✅ Redis connection established successfully")
            break
        except Exception as e:
            print(f"⚠️ Redis connection attempt {attempt + 1} failed:", e)
            await asyncio.sleep(2)
    else:
        raise RuntimeError("❌ Redis is required for price streaming")

    # Start Binance WebSocket manager for all cryptos
    asyncio.create_task(start_crypto_ws())
    print("🚀 Binance WebSocket started for ALL cryptos")

# ----------------- Shutdown Event -----------------
@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Application shutting down... cleaning up.")
    await close_redis()