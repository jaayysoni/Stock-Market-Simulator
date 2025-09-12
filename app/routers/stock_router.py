from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.stock import Stock
from app.services.stock_service import get_multiple_stock_prices

router = APIRouter(
    prefix="/stocks",
    tags=["Stocks"]
)

# Get stock by ID from DB
@router.get("/{stock_id}")
def get_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock

# Get live prices for multiple NSE stocks
@router.get("/prices")
def list_stock_prices(symbols: str = Query("RELIANCE,TCS,INFY")):
    """
    Get current prices of multiple NSE stocks.
    Query parameter `symbols` should be comma-separated, e.g., symbols=RELIANCE,TCS
    """
    symbol_list = symbols.split(",")
    prices = get_multiple_stock_prices(symbol_list)
    return {"prices": prices}

import csv
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent / "data" / "top_500_nse.csv"

def get_all_stock_symbols():
    symbols = []
    with open(DATA_PATH, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            symbols.append(row["Symbol"].upper())
    return symbols

@router.get("/all")
def all_stocks():
    """
    Returns all NSE stock symbols from CSV.
    """
    symbols = get_all_stock_symbols()
    return {"symbols": symbols}