# app/database/init_db.py

from app.database.db import engine, Base
from app.models import stock, portfolio, transaction, user, watchlist  # import all models

def init_db():
    print("📦 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created.")

if __name__ == "__main__":
    init_db()
