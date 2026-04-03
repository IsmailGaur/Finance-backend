"""
models/record_model.py
-----------------------
SQLAlchemy ORM model for the `financial_records` table.

Each record belongs to a user (created_by) and tracks a single
income or expense transaction.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.connection import Base


class FinancialRecord(Base):
    __tablename__ = "financial_records"

    id         = Column(Integer, primary_key=True, index=True)
    amount     = Column(Float, nullable=False)                           # must be > 0
    type       = Column(Enum("income", "expense", name="record_type"),
                        nullable=False)
    category   = Column(String(100), nullable=False, index=True)        # e.g. "salary", "rent"
    date       = Column(DateTime, nullable=False, index=True)            # transaction date
    notes      = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False) # owning user
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # Relationship back to User
    owner = relationship("User", back_populates="records")

    def __repr__(self):
        return (f"<FinancialRecord id={self.id} type={self.type} "
                f"amount={self.amount} category={self.category}>")
