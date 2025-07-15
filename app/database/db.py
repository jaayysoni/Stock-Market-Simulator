# Connects SQLAlchemy to SQLite and initializes engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

#SQLite URL format
DATABASE_URL = "sqlite:///./stock_market.db"

#Create engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

#SessionLocal class for creating sesion objects
SessionLocal1 = sessionmaker(autocommit = False, autoflush = False, bind = engine)

#Base class for model definition
Base = declarative_base()

