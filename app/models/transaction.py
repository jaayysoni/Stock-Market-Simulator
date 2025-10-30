from sqlalchemy import Column, Integer, ForeignKey, Float, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.db import Base  # ✅ unified Base for user_data.db


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}  # avoids table redefinition errors

    id = Column(Integer, primary_key=True, index=True)

    # Reference user by email (Foreign Key)
    user_email = Column(
        String,
        ForeignKey("users.email", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Optional: store username for readability / reports
    user_name = Column(String, nullable=False)

    # Reference to Stock table
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)

    # Core transaction fields
    transaction_type = Column(String, nullable=False)  # "buy" or "sell"
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    stock = relationship("Stock", back_populates="transactions")
    user = relationship("User", backref="transactions")