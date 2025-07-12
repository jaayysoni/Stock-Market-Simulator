# Endpoints for portfolio view, summary, profit/loss
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_portfolio_summary():
    return{"message":"This is your portfolio summary."}

@router.get("/holdings")
async def get_portfolio_holdings():
    return {"message":"These are yourt stock holdings."}