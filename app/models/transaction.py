# Model for buy/sell transactions with timestamps and details
from sqlalchemy import Column,Integer,ForeignKey,Float,String,DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base

class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("user.id"),nullable = False)
    stock_id = Column(Integer, ForeignKey("stock.id"),nullable = False)
    transaction_type = Column(Integer,nullable = False)
    quantity = Column(Integer,nullable = False)
    price = Column(DateTime, default = datetime.utcnow)

    #Realtionships
    user = relationship("User", back_populates = "transactions")
    stock = relationship("stock", back_populates = "transactions")

    