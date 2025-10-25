from pydantic import BaseModel
from datetime import datetime
from enum import Enum


# Enum for transaction type
class TransactionType(str, Enum):
    buy = "buy"
    sell = "sell"


# Schema for creating a transaction
class TransactionCreate(BaseModel):
    stock_id: int
    transaction_type: TransactionType
    quantity: int
    price: float


# Schema for reading transaction data (response)
class TransactionRead(BaseModel):
    id: int
    stock_id: int
    user_id: int
    transaction_type: TransactionType
    quantity: int
    price: float
    timestamp: datetime

    model_config = {
        "from_attributes": True
    }