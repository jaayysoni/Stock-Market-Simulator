# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database.db import engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text 
from app.database.db import Base
from app.models import user,stock,transaction,portfolio,watchlist
from app.routers.auth_router import router as auth_router
from app.routers.stock_router import router as stock_router
from app.routers.transaction_router import router as transaction_router
from app.routers.portfolio_router import router as portfolio_router
from app.config import settings
from app.routers import watchlist_router
from app.routers import google_oauth_router
import os

load_dotenv()

app = FastAPI(
    title="Stock Market Simulator",
    description="Simulate stock trading with virtual money, view portfolios, track transactions, and more.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(stock_router, prefix="/stocks", tags=["Stocks"])
app.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])
app.include_router(watchlist_router.router)
app.include_router(google_oauth_router.router)

@app.get("/")
def root():
    return {"message": "Welcome to the Stock Market Simulator API"}

@app.on_event("startup")
def startup_event():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))  # <-- ✅ Fix this line
            print("Database connected succesfully.")
    except OperationalError as e:
        print("Database connection failed:", e)
        return
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created or already exist.")

@app.on_event("shutdown")
def shutdown_event():
    print("Application is shutting down... cleaning up.")

print("✅ DATABASE_URL:", settings.DATABASE_URL)
print("✅ API_KEY:", settings.API_KEY)
print("✅ DEBUG:", settings.DEBUG)

