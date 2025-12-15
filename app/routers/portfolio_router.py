# app/routers/portfolio_router.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.db import get_user_db as get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.portfolio import Portfolio
from app.models.transaction import Transaction
from app.models.crypto import Crypto
from app.services.price_service import get_all_crypto_prices

router = APIRouter(prefix="/portfolio", tags=["Crypto Portfolio"])

# ==============================
# Buy Crypto
# ==============================
@router.post("/buy")
async def buy_crypto(
    symbol: str = Query(...),
    quantity: float = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    symbol = symbol.upper()
    crypto = db.query(Crypto).filter(Crypto.universal_symbol == symbol).first()
    if not crypto:
        raise HTTPException(status_code=404, detail="Crypto not found")

    prices = await get_all_crypto_prices()
    price_data = next((p for p in prices if p["symbol"] == symbol), None)
    if not price_data or price_data["price"] is None:
        raise HTTPException(status_code=404, detail="Price not available")

    price = price_data["price"]
    total_cost = price * quantity

    if current_user.virtual_balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient virtual balance")

    # Deduct user balance
    current_user.virtual_balance -= total_cost
    db.add(current_user)
    db.commit()

    # Update portfolio
    portfolio_item = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id,
        Portfolio.crypto_id == crypto.id
    ).first()

    if portfolio_item:
        new_qty = portfolio_item.quantity + quantity
        new_avg_price = ((portfolio_item.avg_price * portfolio_item.quantity) + total_cost) / new_qty
        portfolio_item.quantity = new_qty
        portfolio_item.avg_price = new_avg_price
    else:
        portfolio_item = Portfolio(
            user_id=current_user.id,
            crypto_id=crypto.id,
            quantity=quantity,
            avg_price=price
        )
        db.add(portfolio_item)

    # Record transaction
    transaction = Transaction(
        user_id=current_user.id,
        crypto_id=crypto.id,
        quantity=quantity,
        price=price,
        transaction_type="BUY",
        timestamp=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()

    return {"message": f"Bought {quantity} {symbol} at {price} each."}


# ==============================
# Sell Crypto
# ==============================
@router.post("/sell")
async def sell_crypto(
    symbol: str = Query(...),
    quantity: float = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    symbol = symbol.upper()
    crypto = db.query(Crypto).filter(Crypto.universal_symbol == symbol).first()
    if not crypto:
        raise HTTPException(status_code=404, detail="Crypto not found")

    portfolio_item = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id,
        Portfolio.crypto_id == crypto.id
    ).first()
    if not portfolio_item or portfolio_item.quantity < quantity:
        raise HTTPException(status_code=400, detail="Not enough crypto to sell")

    prices = await get_all_crypto_prices()
    price_data = next((p for p in prices if p["symbol"] == symbol), None)
    if not price_data or price_data["price"] is None:
        raise HTTPException(status_code=404, detail="Price not available")

    price = price_data["price"]
    total_earnings = price * quantity

    # Update portfolio
    portfolio_item.quantity -= quantity
    if portfolio_item.quantity == 0:
        db.delete(portfolio_item)

    # Add funds to user balance
    current_user.virtual_balance += total_earnings
    db.add(current_user)
    db.commit()

    # Record transaction
    transaction = Transaction(
        user_id=current_user.id,
        crypto_id=crypto.id,
        quantity=quantity,
        price=price,
        transaction_type="SELL",
        timestamp=datetime.utcnow()
    )
    db.add(transaction)
    db.commit()

    return {"message": f"Sold {quantity} {symbol} at {price} each."}


# ==============================
# Get Portfolio Holdings
# ==============================
@router.get("/holdings")
async def get_portfolio_holdings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio_items = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).all()
    if not portfolio_items:
        return {"message": "No holdings yet."}

    prices_data = await get_all_crypto_prices()
    result = []

    for item in portfolio_items:
        crypto_obj = db.query(Crypto).get(item.crypto_id)
        if not crypto_obj:
            continue
        symbol = crypto_obj.universal_symbol
        price_entry = next((p for p in prices_data if p["symbol"] == symbol), None)
        live_price = price_entry["price"] if price_entry else None
        pl = (live_price - item.avg_price) * item.quantity if live_price else None

        result.append({
            "symbol": symbol,
            "quantity": item.quantity,
            "avg_price": item.avg_price,
            "live_price": live_price,
            "profit_loss": round(pl, 2) if pl is not None else None
        })
    return result


# ==============================
# Transaction History
# ==============================
@router.get("/transactions")
def get_transaction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.timestamp.desc()).all()

    result = []
    for t in transactions:
        crypto_obj = db.query(Crypto).get(t.crypto_id)
        result.append({
            "symbol": crypto_obj.universal_symbol if crypto_obj else None,
            "quantity": t.quantity,
            "price": t.price,
            "type": t.transaction_type.lower(),
            "timestamp": t.timestamp
        })
    return result