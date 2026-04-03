"""
tests/conftest.py
-----------------
Pytest fixtures using SQLite in-memory with StaticPool.
StaticPool ensures ALL connections (including those made by the app
during requests) share the same in-memory database instance.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base
from app.core.deps import get_db
from app.main import app

# StaticPool: every call to connect() returns THE SAME connection.
# This is the only way an in-memory SQLite DB survives across multiple
# SessionLocal() calls within the same process.
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    from app.models import user_model, record_model  # noqa: register models
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client(create_tables):
    app.dependency_overrides[get_db] = override_get_db

    # Seed default admin into the shared in-memory DB
    from app.models.user_model import User
    from app.core.security import hash_password
    db = TestingSession()
    if not db.query(User).filter(User.email == "admin@finance.com").first():
        db.add(User(
            name="Super Admin",
            email="admin@finance.com",
            password=hash_password("Admin1234!"),
            role="admin",
            status="active",
        ))
        db.commit()
    db.close()

    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def admin_token(client):
    r = client.post("/auth/login", data={
        "username": "admin@finance.com",
        "password": "Admin1234!",
    })
    assert r.status_code == 200, f"Login failed: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
