from pydantic import BaseModel, Field

class PortfolioCreate(BaseModel):
    stock_id: int = Field(..., gt=0, example=1)
    quantity: int = Field(..., gt=0, example=10)
    average_price: float = Field(..., gt=0, example=100.5)

class PortfolioRead(BaseModel):
    id: int
    stock_id: int
    user_id: int
    quantity: int
    average_price: float

    class Config:
        orm_mode = True