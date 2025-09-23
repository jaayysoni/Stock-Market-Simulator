# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse,HTMLResponse
import os

from app.database.db import user_engine, UserBase, market_engine, MarketBase
from app.models import user, stock, transaction, portfolio, watchlist
from app.routers.auth_router import router as auth_router
from app.routers.stock_router import router as stock_router
from app.routers.transaction_router import router as transaction_router
from app.routers.portfolio_router import router as portfolio_router
from app.routers import watchlist_router, google_oauth_router
from app.tasks.scheduler import start_scheduler
from app.config import settings

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
app.include_router(stock_router, prefix="/stocks", tags=["Stocks"])
app.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(watchlist_router.router, prefix="/watchlist", tags=["Watchlist"])
app.include_router(google_oauth_router.router, prefix="/oauth", tags=["Google OAuth"])


# ----------------- Pages -----------------
@app.get("/", include_in_schema=False)
def root():
    # return RedirectResponse(url="/static/login.html")
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
@app.on_event("startup")
def startup_event():
    # Check and create tables in user_data.db
    try:
        with user_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        UserBase.metadata.create_all(bind=user_engine)
        print("✅ user_data.db connected and tables ensured.")
    except OperationalError as e:
        print("❌ user_data.db connection failed:", e)

    # Check and create tables in market_data.db
    try:
        with market_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        MarketBase.metadata.create_all(bind=market_engine)
        print("✅ market_data.db connected and tables ensured.")
    except OperationalError as e:
        print("❌ market_data.db connection failed:", e)

    # Start Scheduler
    start_scheduler()
    print("⏰ Scheduler started")

@app.on_event("shutdown")
def shutdown_event():
    print("👋 Application is shutting down... cleaning up.")

# ----------------- Debug Logs -----------------
print("🔗 DATABASE_URL (user):", user_engine.url)
print("🔗 DATABASE_URL (market):", market_engine.url)
print("🔑 API_KEY:", settings.API_KEY)
print("🐞 DEBUG:", settings.DEBUG)