"""
models/user_model.py
---------------------
SQLAlchemy ORM model for the `users` table.

Roles:
  admin   – full CRUD on users + records
  analyst – read records + access summary APIs
  viewer  – read records only

Status:
  active   – can log in
  inactive – blocked (soft delete)
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship

from app.database.connection import Base


class User(Base):
    __tablename__ = "users"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(200), unique=True, index=True, nullable=False)
    password   = Column(String(200), nullable=False)               # bcrypt hash
    role       = Column(Enum("admin", "analyst", "viewer", name="user_roles"),
                        nullable=False, default="viewer")
    status     = Column(Enum("active", "inactive", name="user_status"),
                        nullable=False, default="active")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    # One user → many financial records
    records = relationship("FinancialRecord", back_populates="owner",
                           cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email={self.email} role={self.role}>"
