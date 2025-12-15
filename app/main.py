from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
import asyncio

# ----------------- Internal Imports -----------------
from app.database.db import engine, Base
from app.models import user, transaction, crypto, portfolio
from app.routers import (
    auth_router,
    crypto_router,
    trade_router,
    google_oauth_router,
    portfolio_router
)
from app.services.crypto_ws import start_crypto_ws   # ✅ 1 WS per coin
from app.utils.redis_client import get_redis, close_redis
from app.config import settings

# ----------------- Load Environment -----------------
load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------- FastAPI App -----------------
app = FastAPI(
    title="Crypto Trading Simulator",
    description="Simulate crypto trading with virtual money, view transactions, and more.",
    version="1.0.0"
)

# ----------------- Middleware -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", settings.SECRET_KEY),
    same_site="lax",
    https_only=False
)

# ----------------- Static Files -----------------
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ----------------- Routers -----------------
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(crypto_router.router, prefix="/crypto", tags=["Crypto"])
app.include_router(trade_router.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(portfolio_router.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(google_oauth_router.router, prefix="/oauth", tags=["Google OAuth"])

# ----------------- Pages -----------------
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(BASE_DIR, "static/login.html"))

@app.get("/signup", include_in_schema=False)
def signup_page():
    return FileResponse(os.path.join(BASE_DIR, "static/signup.html"))

@app.get("/dashboard", include_in_schema=False, response_class=HTMLResponse)
def dashboard_page():
    path = os.path.join(BASE_DIR, "static/dashboard.html")
    with open(path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/transactions", include_in_schema=False)
def transactions_page():
    return FileResponse(os.path.join(BASE_DIR, "static/transaction.html"))

@app.get("/tradingterminal", include_in_schema=False)
def trading_terminal_page():
    return FileResponse(os.path.join(BASE_DIR, "static/tradingterminal.html"))

# ----------------- Startup Event -----------------
@app.on_event("startup")
async def startup_event():
    """Initialize DB, Redis, and start Binance WebSocket (1 WS per crypto)"""

    # 1️⃣ Ensure database tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ensured")
    except Exception as e:
        print("❌ Error creating database tables:", e)

    # 2️⃣ Initialize Redis
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

    # 3️⃣ Start Binance WS (1 per crypto)
    asyncio.create_task(start_crypto_ws())
    print("🚀 Binance WebSocket started for ALL cryptos")

# ----------------- Shutdown Event -----------------
@app.on_event("shutdown")
async def shutdown_event():
    print("👋 Application shutting down... cleaning up.")
    await close_redis()