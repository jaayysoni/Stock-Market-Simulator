# CRUD endpoints for stock data, search, watchlist, etc.
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.stock import Stock

router = APIRouter()

@router.get("/stocks/{stock_id}")
def get_stocks(stock_id: int, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.id == stock.id).first()
    if not stock:
        raise HTTPException(status_code=404, detail = "Stock not found")
    return stock