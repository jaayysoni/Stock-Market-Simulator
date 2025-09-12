# app/services/transaction_services.py

from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Transaction, Portfolio, Stock, User
from app.schemas.transaction_schema import TransactionCreate
from app.utils.stock_data import get_stock_price


def buy_stock(db: Session, user: User, data: TransactionCreate) -> Transaction:
    stock_price = get_stock_price(data.symbol)
    total_cost = stock_price * data.quantity

    if user.virtual_balance < total_cost:
        raise ValueError(f"Insufficient virtual balance. Required: ${total_cost:.2f}, Available: ${user.virtual_balance:.2f}")

    # Deduct balance
    user.virtual_balance -= total_cost

    # Record transaction
    transaction = Transaction(
        user_id=user.id,
        stock_symbol=data.symbol,
        quantity=data.quantity,
        price=stock_price,
        type="buy",
        timestamp=datetime.utcnow()
    )
    db.add(transaction)

    # Update or create portfolio entry
    portfolio = db.query(Portfolio).filter_by(user_id=user.id, stock_symbol=data.symbol).first()
    if portfolio:
        old_quantity = portfolio.quantity
        new_quantity = old_quantity + data.quantity
        portfolio.avg_price = ((portfolio.avg_price * old_quantity) + total_cost) / new_quantity
        portfolio.quantity = new_quantity
    else:
        portfolio = Portfolio(
            user_id=user.id,
            stock_symbol=data.symbol,
            quantity=data.quantity,
            avg_price=stock_price
        )
        db.add(portfolio)

    db.commit()
    db.refresh(user)
    return transaction


def sell_stock(db: Session, user: User, data: TransactionCreate) -> Transaction:
    stock_price = get_stock_price(data.symbol)

    portfolio = db.query(Portfolio).filter_by(user_id=user.id, stock_symbol=data.symbol).first()
    if not portfolio or portfolio.quantity < data.quantity:
        raise ValueError(
            f"Not enough shares of {data.symbol} to sell. "
            f"Owned: {portfolio.quantity if portfolio else 0}, Trying to sell: {data.quantity}"
        )

    # Record transaction
    transaction = Transaction(
        user_id=user.id,
        stock_symbol=data.symbol,
        quantity=data.quantity,
        price=stock_price,
        type="sell",
        timestamp=datetime.utcnow()
    )
    db.add(transaction)

    # Update portfolio
    portfolio.quantity -= data.quantity
    if portfolio.quantity == 0:
        db.delete(portfolio)

    db.commit()
    db.refresh(user)