# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import os
import asyncio
from app.routers import market_router
from app.tasks.nifty_tasks import refresh_nifty_cache

from app.routers import ws_router  
from app.database.db import user_engine, UserBase, market_engine, MarketBase
from app.models import user, stock, transaction, portfolio, watchlist
from app.routers.auth_router import router as auth_router
from app.routers.stock_router import router as stock_router
from app.routers.transaction_router import router as transaction_router
from app.routers.portfolio_router import router as portfolio_router
from app.routers import watchlist_router, google_oauth_router
from app.tasks.scheduler import start_scheduler
from app.config import settings
from app.tasks.market_tasks import refresh_market_indices, refresh_top_movers
import asyncio

# 🔹 Import Finnhub WebSocket client
from app.services.finnhub_client import finnhub_client

# ----------------- Load Environment -----------------
load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------- FastAPI App -----------------
app = FastAPI(
    title="Stock Market Simulator",
    description="Simulate stock trading with virtual money, view portfolios, track transactions, and more.",
    version="1.0.0"
)

# ----------------- Middleware -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Static Files -----------------
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ----------------- Routers -----------------
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(stock_router, prefix="/stocks")
app.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(watchlist_router.router, prefix="/watchlist", tags=["Watchlist"])
app.include_router(google_oauth_router.router, prefix="/oauth", tags=["Google OAuth"])
app.include_router(ws_router.router, prefix="/ws", tags=["WebSocket"])
app.include_router(market_router.router, prefix="/market", tags=["Market"])

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

@app.get("/watchlist", include_in_schema=False)
def watchlist_page():
    return FileResponse(os.path.join(BASE_DIR, "static/watchlist.html"))

@app.get("/tradingterminal", include_in_schema=False)
def trading_terminal_page():
    return FileResponse(os.path.join(BASE_DIR, "static/tradingterminal.html"))

# ----------------- Events -----------------
# ----------------- Events -----------------

RUN_FINNHUB_WS = os.getenv("RUN_FINNHUB_WS", "1") == "1"
RUN_YFINANCE = os.getenv("RUN_YFINANCE", "1") == "1"

@app.on_event("startup")
async def startup_event():
    # ✅ Ensure user_data.db tables
    try:
        with user_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        UserBase.metadata.create_all(bind=user_engine)
        print("✅ user_data.db connected and tables ensured.")
    except OperationalError as e:
        print("❌ user_data.db connection failed:", e)

    # ✅ Ensure market_data.db tables
    try:
        with market_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        MarketBase.metadata.create_all(bind=market_engine)
        print("✅ market_data.db connected and tables ensured.")
    except OperationalError as e:
        print("❌ market_data.db connection failed:", e)

    # ⏰ Start Scheduler
    start_scheduler()
    print("⏰ Scheduler started")

    # 📡 Start Finnhub WebSocket in background if allowed
    if RUN_FINNHUB_WS:
        asyncio.create_task(finnhub_client.connect())
        print("📡 Finnhub WebSocket started")
    else:
        print("⚠️ Finnhub WebSocket temporarily halted")

    # 🟢 Start Redis market refresh tasks if allowed (yfinance)
    if RUN_YFINANCE:
        asyncio.create_task(refresh_market_indices())
        asyncio.create_task(refresh_top_movers())
        print("🟢 Redis market indices and top movers tasks started")
    else:
        print("⚠️ yfinance tasks temporarily halted")

    # 🟢 Start Nifty 50 historical cache task (optional, can also halt if needed)
    asyncio.create_task(refresh_nifty_cache())
    print("🟢 Redis market indices, top movers, and Nifty cache tasks started")
@app.on_event("shutdown")
def shutdown_event():
    print("👋 Application is shutting down... cleaning up.")

# ----------------- Debug Logs -----------------
print("🔗 DATABASE_URL (user):", user_engine.url)
print("🔗 DATABASE_URL (market):", market_engine.url)
print("🔑 API_KEY:", settings.API_KEY)
print("🐞 DEBUG:", settings.DEBUG)