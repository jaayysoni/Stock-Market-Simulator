# Schema for stock-related operations

from pydantic import BaseModel
from datetime import datetime

class StockCreate(BaseModel):
    symbol: str
    name : str
    current_price: float

class StockRead(BaseModel):
    id: int
    symbol: str
    name: str
    current_price: float
    update_at: datetime

    class Config:
        orm_mode = True
        