# app/routers/portfolio_router.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict
from datetime import datetime

from app.database.session import get_user_db, get_market_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.portfolio import Portfolio, Transaction
from app.models.stock import Stock
from app.services.stock_service import get_multiple_stock_prices

router = APIRouter(prefix="/portfolio", tags=["Portfolio"])

# ==============================
# Buy Stock
# ==============================
@router.post("/buy")
def buy_stock(
    symbol: str = Query(...),
    quantity: int = Query(...),
    user_db: Session = Depends(get_user_db),
    market_db: Session = Depends(get_market_db),
    current_user: User = Depends(get_current_user)
):
    symbol = symbol.upper()
    stock = market_db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    price_data = get_multiple_stock_prices([symbol])
    if not price_data or price_data[symbol]["price"] is None:
        raise HTTPException(status_code=404, detail="Stock price not available")
    
    price = price_data[symbol]["price"]
    total_cost = price * quantity

    if current_user.cash_balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Deduct cash
    current_user.cash_balance -= total_cost
    user_db.add(current_user)
    user_db.commit()

    # Update portfolio
    portfolio_item = market_db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id,
        Portfolio.stock_id == stock.id
    ).first()

    if portfolio_item:
        new_qty = portfolio_item.quantity + quantity
        new_avg_price = ((portfolio_item.avg_price * portfolio_item.quantity) + total_cost) / new_qty
        portfolio_item.quantity = new_qty
        portfolio_item.avg_price = new_avg_price
    else:
        portfolio_item = Portfolio(
            user_id=current_user.id,
            stock_id=stock.id,
            quantity=quantity,
            avg_price=price
        )
        market_db.add(portfolio_item)

    # Record transaction
    transaction = Transaction(
        user_id=current_user.id,
        stock_id=stock.id,
        quantity=quantity,
        price=price,
        transaction_type="BUY",
        timestamp=datetime.utcnow()
    )
    market_db.add(transaction)
    market_db.commit()

    return {"message": f"Bought {quantity} shares of {symbol} at {price} each."}

# ==============================
# Sell Stock
# ==============================
@router.post("/sell")
def sell_stock(
    symbol: str = Query(...),
    quantity: int = Query(...),
    user_db: Session = Depends(get_user_db),
    market_db: Session = Depends(get_market_db),
    current_user: User = Depends(get_current_user)
):
    symbol = symbol.upper()
    stock = market_db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    portfolio_item = market_db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id,
        Portfolio.stock_id == stock.id
    ).first()
    if not portfolio_item or portfolio_item.quantity < quantity:
        raise HTTPException(status_code=400, detail="Not enough shares to sell")

    price_data = get_multiple_stock_prices([symbol])
    if not price_data or price_data[symbol]["price"] is None:
        raise HTTPException(status_code=404, detail="Stock price not available")

    price = price_data[symbol]["price"]
    total_earnings = price * quantity

    # Update portfolio
    portfolio_item.quantity -= quantity
    if portfolio_item.quantity == 0:
        market_db.delete(portfolio_item)

    # Add cash to user
    current_user.cash_balance += total_earnings
    user_db.add(current_user)
    user_db.commit()

    # Record transaction
    transaction = Transaction(
        user_id=current_user.id,
        stock_id=stock.id,
        quantity=quantity,
        price=price,
        transaction_type="SELL",
        timestamp=datetime.utcnow()
    )
    market_db.add(transaction)
    market_db.commit()

    return {"message": f"Sold {quantity} shares of {symbol} at {price} each."}

# ==============================
# Get Portfolio Holdings
# ==============================
@router.get("/holdings")
def get_portfolio_holdings(
    market_db: Session = Depends(get_market_db),
    current_user: User = Depends(get_current_user)
):
    portfolio_items = market_db.query(Portfolio).filter(
        Portfolio.user_id == current_user.id
    ).all()
    if not portfolio_items:
        return {"message": "No holdings yet."}

    symbols = [item.stock.symbol for item in portfolio_items]
    prices_data = get_multiple_stock_prices(symbols)

    result = []
    for item in portfolio_items:
        live_price = prices_data[item.stock.symbol]["price"] if prices_data.get(item.stock.symbol) else None
        pl = (live_price - item.avg_price) * item.quantity if live_price else None
        result.append({
            "symbol": item.stock.symbol,
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
    market_db: Session = Depends(get_market_db),
    current_user: User = Depends(get_current_user)
):
    transactions = market_db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).order_by(Transaction.timestamp.desc()).all()

    result = []
    for t in transactions:
        result.append({
            "symbol": t.stock.symbol,
            "quantity": t.quantity,
            "price": t.price,
            "type": t.transaction_type,
            "timestamp": t.timestamp
        })
    return result