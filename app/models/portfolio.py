# app/models/portfolio.py
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    crypto_id = Column(Integer, ForeignKey("crypto.id"), nullable=False)
    quantity = Column(Float, default=0.0)

    # Relationships
    user = relationship("User", back_populates="portfolios")
    crypto = relationship("Crypto", back_populates="portfolios")