from pydantic import BaseModel, Field
from datetime import datetime

class StockCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, example="AAPL")
    name: str = Field(..., min_length=1, example="Apple Inc.")
    exchange: str = Field(..., example="NASDAQ")
    price: float = Field(..., gt=0, example=185.67)
    sector: str = Field(..., example="Technology")

class StockRead(BaseModel):
    id: int = Field(..., example=1)
    symbol: str = Field(..., example="AAPL")
    name: str = Field(..., example="Apple Inc.")
    price: float = Field(..., alias="current_price", gt=0, example=185.67)
    updated_at: datetime | None = Field(None, example="2025-07-16T12:00:00Z")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }