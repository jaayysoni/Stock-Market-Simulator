# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database.db import engine
from sqlalchemy.exc import OperationalError
from app.routers.auth_router import router as auth_router
from app.routers.stock_router import router as stock_router
from app.routers.transaction_router import router as transaction_router
from app.routers.portfolio_router import router as portfolio_router
from app.config import settings
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Stock Market Simulator",
    description="Simulate stock trading with virtual money, view portfolios, track transactions, and more.",
    version="1.0.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev. Later, restrict to your frontend URL.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(stock_router, prefix="/stocks", tags=["Stocks"])
app.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["Portfolio"])

# Root route
@app.get("/")
def root():
    return {"message": "Welcome to the Stock Market Simulator API"}

# Startup event
@app.on_event("startup")
def startup_event():
    try:
        #Testing DB connection startup
        with engine.connect() as conn:
            conn.execute("SELECT 1")
            print("Database connected succesfully.")
    except OperationalError as e:
            print("Database connection failed:",e)

# Shutdown event
@app.on_event("shutdown")
def shutdown_event():
     #you can close DB connection or clean up tasks here
     print("Application is shutting dowm... clearimng up.")

# TEMP: Print settings to verify loading
print("✅ DATABASE_URL:", settings.DATABASE_URL)
print("✅ API_KEY:", settings.API_KEY)
print("✅ DEBUG:", settings.DEBUG)
    # between these two comments