"""
tests/test_auth.py
-------------------
Tests for authentication endpoints: login, token validation, /auth/me.
"""


def test_health_check(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_login_success(client):
    r = client.post("/auth/login", data={
        "username": "admin@finance.com",
        "password": "Admin1234!",
    })
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["user"]["role"] == "admin"


def test_login_wrong_password(client):
    r = client.post("/auth/login", data={
        "username": "admin@finance.com",
        "password": "WrongPass999!",
    })
    assert r.status_code == 401


def test_login_unknown_email(client):
    r = client.post("/auth/login", data={
        "username": "nobody@example.com",
        "password": "SomePass1!",
    })
    assert r.status_code == 401


def test_me_returns_current_user(client, admin_headers):
    r = client.get("/auth/me", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "admin@finance.com"


def test_me_without_token_returns_401(client):
    r = client.get("/auth/me")
    assert r.status_code == 401


def test_me_with_invalid_token_returns_401(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer fake.token.here"})
    assert r.status_code == 401
