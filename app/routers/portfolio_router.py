from fastapi import APIRouter
from sqlalchemy import func, case
from app.database.db import SessionLocal
from app.models.transaction import Transaction
from app.utils.cache import get_crypto_prices  # use snapshot cache

router = APIRouter(prefix="/portfolio", tags=["Crypto Portfolio"])

# -----------------------------
# Portfolio Holdings (unsold crypto)
# -----------------------------
@router.get("/holdings")
async def get_portfolio_holdings():
    """
    Returns unsold crypto holdings for the universal user (user_id=1)
    with average buy price, live price, and P/L.
    """
    db = SessionLocal()
    try:
        # Aggregate net unsold quantities
        rows = db.query(
            Transaction.symbol,
            func.sum(
                case(
                    (Transaction.transaction_type == "BUY", Transaction.quantity),
                    else_=-Transaction.quantity
                )
            ).label("quantity")
        ).filter(Transaction.user_id == 1).group_by(Transaction.symbol).having(
            func.sum(
                case(
                    (Transaction.transaction_type == "BUY", Transaction.quantity),
                    else_=-Transaction.quantity
                )
            ) > 0
        ).all()

        if not rows:
            return {"holdings": []}

        # Get live prices from snapshot cache
        prices_data = await get_crypto_prices() or []

        portfolio = [
            {
                "symbol": r.symbol,
                "quantity": round(r.quantity, 8),
                "avg_price": round(db.query(
                    func.sum(Transaction.quantity * Transaction.price) / func.sum(Transaction.quantity)
                ).filter(
                    Transaction.user_id == 1,
                    Transaction.symbol == r.symbol,
                    Transaction.transaction_type == "BUY"
                ).scalar(), 2),
                "live_price": next((p["price"] for p in prices_data if p["binance_symbol"] == r.symbol), None),
            } for r in rows
        ]

        # Calculate P/L
        for p in portfolio:
            if p["live_price"] is not None:
                p["profit_loss"] = round((p["live_price"] - p["avg_price"]) * p["quantity"], 2)
            else:
                p["profit_loss"] = None

        return {"holdings": portfolio}
    finally:
        db.close()


# -----------------------------
# Transaction History
# -----------------------------
@router.get("/transactions")
def get_transaction_history():
    """
    Returns all transactions of the universal user (user_id=1)
    """
    db = SessionLocal()
    try:
        transactions = db.query(Transaction).filter(
            Transaction.user_id == 1
        ).order_by(Transaction.created_at.desc()).all()

        return [
            {
                "symbol": t.symbol,
                "quantity": t.quantity,
                "price": t.price,
                "type": t.transaction_type.lower(),
                "timestamp": t.created_at
            } for t in transactions
        ]
    finally:
        db.close()