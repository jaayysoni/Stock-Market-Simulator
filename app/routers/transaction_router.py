# Buy/sell actions, filters, history endpoints
from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_all_transactions():
    return{"message":"There are all your past transactions"}

@router.post("/buy")
async def buy_stock():
    return {"message":"stock bought succesfully"}

@router.post("/sell")
async def sell_stock():
    return{"message":"Stock sold succesfully"}

