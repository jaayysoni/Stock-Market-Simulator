# app/create_tables.py

from app.database.db import UserBase, user_engine
from app.models.user import User
from app.models.portfolio import Portfolio  # import other models as needed

# Create all tables in the USER database
UserBase.metadata.create_all(bind=user_engine)
print("User tables created successfully.")