# app/services/transaction_services.py

from sqlalchemy.orm import Session
from datetime import datetime
from app.models.transaction import Transaction
from app.models.portfolio import Portfolio
from app.models.crypto import Crypto
from app.models.user import User
from app.schemas.transaction_schema import TransactionCreate
from app.services.price_service import get_all_crypto_prices


async def buy_crypto(db: Session, user: User, data: TransactionCreate) -> Transaction:
    """
    Handles buying crypto and updating portfolio.
    """

    # 1️⃣ Fetch live prices
    prices = await get_all_crypto_prices()
    crypto_price_map = {c["symbol"]: c["price"] for c in prices}
    price = data.price or crypto_price_map.get(data.crypto_symbol)

    if price is None:
        raise ValueError(f"Price not found for crypto: {data.crypto_symbol}")

    total_cost = price * data.quantity

    if user.virtual_balance < total_cost:
        raise ValueError(
            f"Insufficient virtual balance. Required: {total_cost}, Available: {user.virtual_balance}"
        )

    # Deduct user balance
    user.virtual_balance -= total_cost
    db.add(user)

    # 2️⃣ Get crypto object from DB
    crypto = db.query(Crypto).filter(Crypto.universal_symbol == data.crypto_symbol).first()
    if not crypto:
        raise ValueError(f"Crypto {data.crypto_symbol} not found in DB")

    # 3️⃣ Record transaction
    transaction = Transaction(
        user_id=user.id,
        crypto_id=crypto.id,
        transaction_type="BUY",
        quantity=data.quantity,
        price=price,
        timestamp=data.timestamp or datetime.utcnow(),
    )
    db.add(transaction)

    # 4️⃣ Update or create portfolio entry
    portfolio = db.query(Portfolio).filter_by(user_id=user.id, crypto_id=crypto.id).first()
    if portfolio:
        old_quantity = portfolio.quantity
        new_quantity = old_quantity + data.quantity
        # Weighted average price
        portfolio.avg_price = ((portfolio.avg_price * old_quantity) + total_cost) / new_quantity
        portfolio.quantity = new_quantity
    else:
        portfolio = Portfolio(
            user_id=user.id,
            crypto_id=crypto.id,
            quantity=data.quantity,
            avg_price=price,
        )
        db.add(portfolio)

    # Commit all changes
    db.commit()
    db.refresh(transaction)
    return transaction


async def sell_crypto(db: Session, user: User, data: TransactionCreate) -> Transaction:
    """
    Handles selling crypto and updating portfolio.
    """

    # 1️⃣ Fetch live prices
    prices = await get_all_crypto_prices()
    crypto_price_map = {c["symbol"]: c["price"] for c in prices}
    price = data.price or crypto_price_map.get(data.crypto_symbol)

    if price is None:
        raise ValueError(f"Price not found for crypto: {data.crypto_symbol}")

    # 2️⃣ Get crypto object
    crypto = db.query(Crypto).filter(Crypto.universal_symbol == data.crypto_symbol).first()
    if not crypto:
        raise ValueError(f"Crypto {data.crypto_symbol} not found in DB")

    # 3️⃣ Fetch portfolio entry
    portfolio = db.query(Portfolio).filter_by(user_id=user.id, crypto_id=crypto.id).first()
    if not portfolio or portfolio.quantity < data.quantity:
        raise ValueError(
            f"Not enough crypto to sell. Owned: {portfolio.quantity if portfolio else 0}, Trying to sell: {data.quantity}"
        )

    # 4️⃣ Record transaction
    transaction = Transaction(
        user_id=user.id,
        crypto_id=crypto.id,
        transaction_type="SELL",
        quantity=data.quantity,
        price=price,
        timestamp=data.timestamp or datetime.utcnow(),
    )
    db.add(transaction)

    # 5️⃣ Update portfolio
    portfolio.quantity -= data.quantity
    if portfolio.quantity == 0:
        db.delete(portfolio)

    # 6️⃣ Add funds back to user
    user.virtual_balance += price * data.quantity
    db.add(user)

    db.commit()
    db.refresh(transaction)
    return transaction