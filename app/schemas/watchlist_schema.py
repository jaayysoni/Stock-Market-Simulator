from pydantic import BaseModel
from typing import Optional

# Request schema: used when adding a new stock to the watchlist
class WatchlistCreate(BaseModel):
    stock_id: int  # assuming you're using stock_id instead of symbol directly

# Minimal response schema
class WatchlistOut(BaseModel):
    id: int
    stock_id: int

    class Config:
        orm_mode = True

# Optional: detailed nested stock info if you're returning stock details in response
class StockInWatchlist(BaseModel):
    id: int
    symbol: str
    name: str
    price: float

    class Config:
        orm_mode = True

# Full watchlist read schema with nested stock and user info (optional)
class WatchlistRead(BaseModel):
    id: int
    user_id: int
    stock: Optional[StockInWatchlist]  # nested stock info if joined in query

    class Config:
        orm_mode = True