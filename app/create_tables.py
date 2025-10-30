from app.database.db import engine, Base
from app.models import user, stock, portfolio, transaction, watchlist

print("⏳ Creating tables in user_data.db ...")
Base.metadata.create_all(bind=engine)
print("✅ All tables created successfully!")