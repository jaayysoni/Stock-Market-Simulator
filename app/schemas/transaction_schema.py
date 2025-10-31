from pydantic import BaseModel, field_validator
from datetime import datetime
from enum import Enum
from typing import Optional


# ✅ Enum for transaction type (expected lowercase)
class TransactionType(str, Enum):
    buy = "buy"
    sell = "sell"


# ✅ Schema for creating a transaction
class TransactionCreate(BaseModel):
    stock_id: int
    transaction_type: TransactionType
    quantity: int
    price: Optional[float] = None  # Can be fetched in service if not provided
    timestamp: Optional[datetime] = None  # Optional, set current time if not provided


# ✅ Schema for reading transaction data (response)
class TransactionRead(BaseModel):
    id: int
    stock_id: int
    user_email: str
    user_name: str
    transaction_type: TransactionType
    quantity: int
    price: float
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }

    # ✅ Convert "BUY"/"SELL" → "buy"/"sell" before validation
    @field_validator("transaction_type", mode="before")
    def normalize_transaction_type(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v