from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os 

# to load enviornment variable variable from .env
load_dotenv()

#to import your routers here (as you build them)
#from app.routers import auth_router, stock_router, etc.

#initialize FastAPI app
app = FastAPI(
    title = "Stock-Market-Simulator",
    description = "An Simulator for Learning from Virtual Money ",
    version = "1.0.0"
)

#Enabeling CORS (cross-original Resuorce Sharing) for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

#startup Event
@app.on_event("startup")
async def on_startup():
    print("FASTAPI application Started!")

#shutdown event
@app.on_event("shutdown")
async def on_shutdown():
    print("FASTAPI application shutting down!")

# Test root route
@app.get("/")
async def root():
    return {"message": "Welcome to the Stock Market Simulator API"}

