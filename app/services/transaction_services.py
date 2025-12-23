# app/services/transaction_services.py

from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.crypto import Crypto

# ----------------------------
# TRANSACTION SERVICE (UNIVERSAL USER)
# ----------------------------

def get_transactions(db: Session) -> list[dict]:
    """
    Returns all transactions of the universal user.
    Each transaction includes crypto symbol, type, quantity, price, and timestamp.
    """
    transactions = db.query(Transaction).order_by(Transaction.timestamp).all()
    result = []

    for tx in transactions:
        crypto = db.query(Crypto).filter(Crypto.id == tx.crypto_id).first()
        if not crypto:
            continue

        result.append({
            "crypto_symbol": crypto.universal_symbol,
            "transaction_type": tx.transaction_type,
            "quantity": tx.quantity,
            "price": tx.price,
            "timestamp": tx.timestamp
        })

    return result