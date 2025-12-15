from sqlalchemy import Column, Integer, String
from app.database.db import Base

class Crypto(Base):
    __tablename__ = "crypto"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    universal_symbol = Column(String, unique=True, nullable=False)
    binance_symbol = Column(String, nullable=False)