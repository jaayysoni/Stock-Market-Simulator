# app/routers/watchlist_router.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.watchlist import Watchlist

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

@router.post("/add")
def add_to_watchlist(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if already exists
    existing = db.query(Watchlist).filter_by(user_id=current_user.id, symbol=symbol).first()
    if existing:
        raise HTTPException(status_code=400, detail="Stock already in watchlist")

    entry = Watchlist(user_id=current_user.id, symbol=symbol.upper())
    db.add(entry)
    db.commit()
    return {"message": f"{symbol.upper()} added to watchlist."}

@router.get("/")
def get_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entries = db.query(Watchlist).filter_by(user_id=current_user.id).all()
    return {"watchlist": [entry.symbol for entry in entries]}

@router.delete("/remove")
def remove_from_watchlist(
    symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = db.query(Watchlist).filter_by(user_id=current_user.id, symbol=symbol.upper()).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Stock not found in watchlist")

    db.delete(entry)
    db.commit()
    return {"message": f"{symbol.upper()} removed from watchlist."}