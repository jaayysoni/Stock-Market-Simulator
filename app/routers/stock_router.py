# CRUD endpoints for stock data, search, watchlist, etc.
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_all_stocks():
    return{"message": "List of all stocks will be returned heree"}