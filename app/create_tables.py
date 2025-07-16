# create_tables.py

from app.database.db import engine
from app.database.db import Base
from app.models.stock import Stock  # Import all models you want to create tables for


# Create the tables
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")