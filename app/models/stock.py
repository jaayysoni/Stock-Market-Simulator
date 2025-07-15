 # Stock model with symbol, name, latest price, sector, etc.
from sqlalchemy import Column, Integer, String, Float
from app.database.db import Base

class Stock(Base):
    __tablename__ = "stocks"

id = Column(Integer, primary_Key = True, index = True)
name = Column(String,nullable = False)
symbol = Column(String,unique = True, index = True, nullable = False)
exchange = Column(String,index = True)
price = Column(Float,nullable = False)
sector = Column(String)

def __repr__(self):
    return f"<Stock(name={self.name}, symbol={self.symbol}, price={self.price})>"


