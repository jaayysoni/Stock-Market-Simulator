# app/routers/watchlist_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from app.database.session import get_user_db
from app.models.watchlist import Watchlist
from app.schemas.watchlist_schema import WatchlistCreate, WatchlistOut
from app.auth.oauth import get_current_user
from app.models.user import User
from app.services.stock_service import get_multiple_stock_prices

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

# ==============================
# Add stock to watchlist
# ==============================
@router.post("/", response_model=WatchlistOut)
def add_to_watchlist(
    watch_data: WatchlistCreate,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    existing = db.query(Watchlist).filter_by(
        user_id=current_user.id,
        symbol=watch_data.symbol.upper()
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")

    watch = Watchlist(user_id=current_user.id, symbol=watch_data.symbol.upper())
    db.add(watch)
    db.commit()
    db.refresh(watch)
    return watch

# ==============================
# Get all watchlist stocks
# ==============================
@router.get("/", response_model=List[WatchlistOut])
def get_watchlist(
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Watchlist).filter_by(user_id=current_user.id).all()

# ==============================
# Remove stock from watchlist
# ==============================
@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(
    symbol: str,
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    watch = db.query(Watchlist).filter_by(
        user_id=current_user.id,
        symbol=symbol.upper()
    ).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Stock not found in watchlist")

    db.delete(watch)
    db.commit()
    return

# ==============================
# Get live prices for all watchlist stocks
# ==============================
@router.get("/prices", response_model=Dict[str, Dict[str, Optional[float]]])
def get_watchlist_prices(
    db: Session = Depends(get_user_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch live prices for all stocks in the user's watchlist.
    """
    items = db.query(Watchlist).filter_by(user_id=current_user.id).all()
    if not items:
        return {"message": "Watchlist is empty"}

    symbols = [item.symbol for item in items]

    try:
        prices = get_multiple_stock_prices(symbols)
        return {"prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch prices: {e}")