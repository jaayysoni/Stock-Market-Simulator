# app/routers/portfolio_router.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy import case, func

from app.database.db import get_user_db as get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.transaction import Transaction
from app.services.price_service import get_all_crypto_prices

# Remove prefix from the router
router = APIRouter(tags=["Crypto Portfolio"])

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

    # Record transaction
    transaction = Transaction(
        user_id=current_user.id,
        symbol=symbol,
        quantity=quantity,
        price=price,
        transaction_type="BUY",
        created_at=datetime.utcnow()
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

    # Check current holdings (unsold crypto)
    holding = db.query(
        func.sum(
            case(
                (Transaction.transaction_type == "BUY", Transaction.quantity),
                else_=-Transaction.quantity
            )
        )
    ).filter(Transaction.user_id == current_user.id, Transaction.symbol == symbol).scalar() or 0

    if holding < quantity:
        raise HTTPException(status_code=400, detail="Not enough crypto to sell")

    prices = await get_all_crypto_prices()
    price_data = next((p for p in prices if p["symbol"] == symbol), None)
    if not price_data or price_data["price"] is None:
        raise HTTPException(status_code=404, detail="Price not available")

    price = price_data["price"]
    total_earnings = price * quantity

    # Add funds to user balance
    current_user.virtual_balance += total_earnings
    db.add(current_user)

    # Record transaction
    transaction = Transaction(
        user_id=current_user.id,
        symbol=symbol,
        quantity=quantity,
        price=price,
        transaction_type="SELL",
        created_at=datetime.utcnow()
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
    # Aggregate unsold crypto
    rows = db.query(
        Transaction.symbol,
        func.sum(
            case(
                (Transaction.transaction_type == "BUY", Transaction.quantity),
                else_=-Transaction.quantity
            )
        ).label("quantity")
    ).filter(Transaction.user_id == current_user.id).group_by(Transaction.symbol).having(func.sum(
        case(
            (Transaction.transaction_type == "BUY", Transaction.quantity),
            else_=-Transaction.quantity
        )
    ) > 0).all()

    if not rows:
        return {"message": "No holdings yet."}

    prices_data = await get_all_crypto_prices()
    portfolio = []

    for r in rows:
        # Calculate average buy price
        avg_price = db.query(
            func.sum(Transaction.quantity * Transaction.price) / func.sum(Transaction.quantity)
        ).filter(
            Transaction.user_id == current_user.id,
            Transaction.symbol == r.symbol,
            Transaction.transaction_type == "BUY"
        ).scalar()

        # Live price
        price_entry = next((p for p in prices_data if p["symbol"] == r.symbol), None)
        live_price = price_entry["price"] if price_entry else None
        pl = (live_price - avg_price) * r.quantity if live_price else None

        portfolio.append({
            "symbol": r.symbol,
            "quantity": round(r.quantity, 8),
            "avg_price": round(avg_price, 2),
            "live_price": live_price,
            "profit_loss": round(pl, 2) if pl is not None else None
        })

    return {"holdings": portfolio}


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
    ).order_by(Transaction.created_at.desc()).all()

    result = []
    for t in transactions:
        result.append({
            "symbol": t.symbol,
            "quantity": t.quantity,
            "price": t.price,
            "type": t.transaction_type.lower(),
            "timestamp": t.created_at
        })
    return result
