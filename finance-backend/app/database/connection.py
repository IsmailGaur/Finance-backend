"""
database/connection.py
-----------------------
SQLAlchemy engine and session factory.
All models import `Base` from here so they share the same metadata object,
which allows `Base.metadata.create_all(engine)` to create every table at once.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import get_settings

settings = get_settings()

# SQLite needs connect_args for thread safety in FastAPI (multi-threaded ASGI)
connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,          # log SQL statements when DEBUG=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


def init_db() -> None:
    """Create all tables that don't yet exist. Called once at startup."""
    # Import models so SQLAlchemy registers them before create_all
    from app.models import user_model, record_model  # noqa: F401
    Base.metadata.create_all(bind=engine)
