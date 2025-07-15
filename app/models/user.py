# User model with fields like id, email, password, etc.
from sqlalchemy import Column, Integer, String, Float
from app.database.db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key = True,index = True)
    email = Column(String,unique = True, index = True)
    password = Column(String)
    username = Column(String, index = True)
    virtual_balance = Column(Float, default = 100000.0)
    