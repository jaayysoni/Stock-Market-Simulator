# Schema for transaction requests/responses
from pydantic import BaseModel
from datetime import datetime

class TransactionCreate(BaseModel):
    stock_id: int
    user_id: int
    transaction_type: str
    quantity: int
    price: float

class TransactionRead(BaseModel):
    id: int
    stock_id: int
    user_id: int
    transaction_type = str
    quantity: int
    price: float
    timestamp: datetime

    class Config:
        orm_mode = True
        