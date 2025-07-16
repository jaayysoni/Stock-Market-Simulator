# Model to track user's stock holdings and portfolio metrics
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable = False)
    stock_id = Column(Integer, ForeignKey("stock.id"), nullable = False)
    stock_id = Column(Integer,ForeignKey("stock.id"),nullable = False)
    quantity = Column(Integer, nullable = False)

    #Relationship
    user = relationship("User",back_populates = "portfolios")
    stock = relationship("Stock", back_populates = "portfolios")
    