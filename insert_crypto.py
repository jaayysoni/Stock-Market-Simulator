import csv
from sqlalchemy.exc import IntegrityError
from app.database.db import Base, engine, SessionLocal
from app.models.crypto import Crypto

Base.metadata.create_all(bind=engine)
print("✅ Crypto table ensured")

CSV_FILE = "/Users/jaysoni/Downloads/crypto.csv"

def insert_crypto_from_csv():
    db = SessionLocal()
    inserted = 0
    skipped = 0

    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)

            for row in reader:
                if len(row) < 3:
                    continue

                coin = Crypto(
                    name=row[0].strip(),
                    universal_symbol=row[1].strip(),
                    binance_symbol=row[2].strip()
                )

                try:
                    db.add(coin)
                    db.commit()
                    inserted += 1
                except IntegrityError:
                    db.rollback()
                    skipped += 1

        print(f"✅ Inserted: {inserted}, Skipped duplicates: {skipped}")

    finally:
        db.close()

insert_crypto_from_csv()