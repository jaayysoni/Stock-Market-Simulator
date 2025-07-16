from pydantic import BaseModel

class PortfolioRead(BaseModel):
    id: int
    stock_id: int
    user_id = int
    average_price: float

    class Config:
        orm_mode = True
        