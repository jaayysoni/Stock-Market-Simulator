# app/main.py

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
import os
import asyncio

# ----------------- Internal Imports -----------------
from app.database.db import engine, Base
from app.models import user, stock, transaction, watchlist
from app.routers.auth_router import router as auth_router
from app.routers.stock_router import router as stock_router
from app.routers.transaction_router import router as transaction_router
from app.routers import watchlist_router, google_oauth_router, market_router, ws_router
from app.tasks.scheduler import start_scheduler
from app.tasks.market_tasks import refresh_market_indices, refresh_top_movers
from app.tasks.nifty_tasks import refresh_nifty_cache
from app.services.finnhub_client import finnhub_client
from app.config import settings

# ----------------- Load Environment -----------------
load_dotenv()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ----------------- FastAPI App -----------------
app = FastAPI(
    title="Stock Market Simulator",
    description="Simulate stock trading with virtual money, view transactions, and more.",
    version="1.0.0"
)

# ----------------- Middleware -----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "super-secret-key"),
    same_site="lax",
    https_only=False,  # ✅ Local testing allowed
)

# ----------------- Static Files -----------------
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ----------------- Routers -----------------
# ✅ Clean, consistent prefixing
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(stock_router, prefix="/stocks", tags=["Stocks"])
app.include_router(transaction_router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(watchlist_router.router, prefix="/watchlist", tags=["Watchlist"])
app.include_router(google_oauth_router.router, prefix="/oauth", tags=["Google OAuth"])
app.include_router(ws_router.router, prefix="/ws", tags=["WebSocket"])
app.include_router(market_router.router, prefix="/market", tags=["Market"])

# ----------------- Pages -----------------
@app.get("/", include_in_schema=False)
def root():
    """Landing page - redirects to login"""
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

@app.get("/transactions", include_in_schema=False)
def transactions_page():
    """Transactions page - no strict auth dependency for now"""
    return FileResponse(os.path.join(BASE_DIR, "static/transaction.html"))

@app.get("/tradingterminal", include_in_schema=False)
def trading_terminal_page():
    return FileResponse(os.path.join(BASE_DIR, "static/tradingterminal.html"))

# ----------------- Environment Flags -----------------
RUN_FINNHUB_WS = os.getenv("RUN_FINNHUB_WS", "1") == "1"
RUN_YFINANCE = os.getenv("RUN_YFINANCE", "1") == "1"

# ----------------- Startup Event -----------------
@app.on_event("startup")
async def startup_event():
    """Initialize DB and start background tasks"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
        print("✅ Database connected and tables ensured.")
    except OperationalError as e:
        print("❌ Database connection failed:", e)

    # ⏰ Start Scheduler
    start_scheduler()
    print("⏰ Scheduler started")

    # 📡 Start Finnhub WebSocket
    if RUN_FINNHUB_WS:
        asyncio.create_task(finnhub_client.connect())
        print("📡 Finnhub WebSocket started")
    else:
        print("⚠️ Finnhub WebSocket temporarily disabled")

    # 🟢 Start market tasks
    if RUN_YFINANCE:
        asyncio.create_task(refresh_market_indices())
        asyncio.create_task(refresh_top_movers())
        print("🟢 Market indices and top movers tasks started")
    else:
        print("⚠️ yfinance tasks temporarily disabled")

    # 🟢 Start Nifty 50 cache refresh
    asyncio.create_task(refresh_nifty_cache())
    print("🟢 Nifty 50 cache refresh started")

# ----------------- Shutdown Event -----------------
@app.on_event("shutdown")
def shutdown_event():
    print("👋 Application shutting down... cleaning up.")

# ----------------- Debug Logs -----------------
print("🔗 DATABASE_URL:", engine.url)
print("🔑 API_KEY:", settings.API_KEY)
print("🐞 DEBUG:", settings.DEBUG)