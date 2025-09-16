# app/routers/watchlist_router.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.db import get_user_db
from app.models.watchlist import Watchlist
from app.schemas.watchlist_schema import WatchlistCreate, WatchlistOut
from app.auth.oauth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

@router.post("/", response_model=WatchlistOut)
def add_to_watchlist(watch_data: WatchlistCreate, db: Session = Depends(get_user_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Watchlist).filter_by(user_id=current_user.id, symbol=watch_data.symbol).first()
    if existing:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")
    watch = Watchlist(user_id=current_user.id, symbol=watch_data.symbol)
    db.add(watch)
    db.commit()
    db.refresh(watch)
    return watch

@router.get("/", response_model=list[WatchlistOut])
def get_watchlist(db: Session = Depends(get_user_db), current_user: User = Depends(get_current_user)):
    return db.query(Watchlist).filter_by(user_id=current_user.id).all()

@router.delete("/{symbol}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_watchlist(symbol: str, db: Session = Depends(get_user_db), current_user: User = Depends(get_current_user)):
    watch = db.query(Watchlist).filter_by(user_id=current_user.id, symbol=symbol).first()
    if not watch:
        raise HTTPException(status_code=404, detail="Stock not found in watchlist")
    db.delete(watch)
    db.commit()
    return