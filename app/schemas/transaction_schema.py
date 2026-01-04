from pydantic import BaseModel, field_validator
from datetime import datetime
from enum import Enum
from typing import Optional

# =========================
# Transaction Type Enum
# =========================
class TransactionType(str, Enum):
    buy = "buy"
    sell = "sell"

# =========================
# Transaction Create Schema
# =========================
class TransactionCreate(BaseModel):
    user_id: int
    symbol: str
    transaction_type: TransactionType
    quantity: float
    price: Optional[float] = None
    crypto_id: Optional[int] = None
    timestamp: Optional[datetime] = None

    @field_validator("transaction_type", mode="before")
    def normalize_transaction_type(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v

# =========================
# Transaction Read Schema
# =========================
class TransactionRead(BaseModel):
    id: int
    user_id: int
    symbol: str
    transaction_type: TransactionType
    quantity: float
    price: float
    created_at: Optional[datetime] = None
    crypto_id: Optional[int] = None
    timestamp: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @field_validator("transaction_type", mode="before")
    def normalize_transaction_type(cls, v):
        if isinstance(v, str):
            return v.lower()
        return v