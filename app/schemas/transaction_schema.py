from pydantic import BaseModel
from datetime import datetime
from enum import Enum

# Optional but better for validation
class TransactionType(str, Enum):
    buy = "buy"
    sell = "sell"

class TransactionCreate(BaseModel):
    stock_id: int
    user_id: int
    transaction_type: TransactionType  # was str
    quantity: int
    price: float

class TransactionRead(BaseModel):
    id: int
    stock_id: int
    user_id: int
    transaction_type: TransactionType  # FIXED: use colon instead of '='
    quantity: int
    price: float
    timestamp: datetime

    class Config:
        orm_mode = True