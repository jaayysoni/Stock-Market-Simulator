# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from tests import test_auth

from app.database.db import engine, Base
from app.models import user, stock, transaction, portfolio, watchlist
from app.routers.auth_router import router as auth_router
from app.routers.stock_router import router as stock_router
from app.routers.transaction_router import router as transaction_router
from app.routers.portfolio_router import router as portfolio_router
from app.routers import watchlist_router, google_oauth_router
from app.tasks.scheduler import start_scheduler
from app.config import settings
import os

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Stock Market Simulator",
    description="Simulate stock trading with virtual money, view portfolios, track transactions, and more.",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(stock_router, prefix="/stocks", tags=["Stocks"])
app.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(watchlist_router.router)
app.include_router(google_oauth_router.router)
app.include_router(test_auth.router)  # Keep for testing

# Root & Pages
@app.get("/")
def root():
    return RedirectResponse(url="/static/login.html")

@app.get("/signup")
def signup_page():
    return FileResponse(os.path.join(BASE_DIR, "static/signup.html"))

@app.get("/dashboard")
def dashboard_page():
    return FileResponse(os.path.join(BASE_DIR, "static/dashboard.html"))

# Startup Event
@app.on_event("startup")
def startup_event():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("Database connected successfully.")
    except OperationalError as e:
        print("Database connection failed:", e)
        return

    Base.metadata.create_all(bind=engine)
    print("✅ All tables created or already exist.")

    # Start Scheduler
    start_scheduler()
    print("⏰ Scheduler started")

# Shutdown Event
@app.on_event("shutdown")
def shutdown_event():
    print("Application is shutting down... cleaning up.")

@app.get("/watchlist")
def watchlist_page():
    return FileResponse(os.path.join(BASE_DIR, "static/watchlist.html"))


@app.get("/tradingterminal")
def watchlist_page():
    return FileResponse(os.path.join(BASE_DIR, "static/tradingterminal.html"))
# Environment Logs
print("✅ DATABASE_URL:", settings.DATABASE_URL)
print("✅ API_KEY:", settings.API_KEY)
print("✅ DEBUG:", settings.DEBUG)