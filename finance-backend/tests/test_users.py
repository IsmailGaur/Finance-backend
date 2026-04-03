"""
tests/test_users.py
--------------------
Tests for user management: CRUD operations, role enforcement,
duplicate detection, and soft-delete behaviour.
"""

import pytest


# ── Helper ────────────────────────────────────────────────────────────────────

def make_user(client, headers, suffix, role="viewer"):
    return client.post("/users/", json={
        "name":     f"Test {suffix}",
        "email":    f"test_{suffix}@example.com",
        "password": "TestPass1!",
        "role":     role,
        "status":   "active",
    }, headers=headers)


# ── Create ────────────────────────────────────────────────────────────────────

def test_admin_can_create_user(client, admin_headers):
    r = make_user(client, admin_headers, "create_ok")
    assert r.status_code == 201
    body = r.json()
    assert body["role"] == "viewer"
    assert "password" not in body          # password must never be returned


def test_duplicate_email_returns_409(client, admin_headers):
    make_user(client, admin_headers, "dup")
    r = make_user(client, admin_headers, "dup")
    assert r.status_code == 409


def test_create_user_missing_fields_returns_422(client, admin_headers):
    r = client.post("/users/", json={"name": "Incomplete"},
                    headers=admin_headers)
    assert r.status_code == 422


def test_weak_password_returns_422(client, admin_headers):
    r = client.post("/users/", json={
        "name": "Weak", "email": "weak@example.com",
        "password": "short",  # no uppercase, no digit, too short
        "role": "viewer", "status": "active",
    }, headers=admin_headers)
    assert r.status_code == 422


# ── Read ──────────────────────────────────────────────────────────────────────

def test_admin_can_list_users(client, admin_headers):
    r = client.get("/users/", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_user_by_id(client, admin_headers):
    created = make_user(client, admin_headers, "getbyid").json()
    r = client.get(f"/users/{created['id']}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["id"] == created["id"]


def test_get_nonexistent_user_returns_404(client, admin_headers):
    r = client.get("/users/999999", headers=admin_headers)
    assert r.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────

def test_admin_can_update_user_role(client, admin_headers):
    user = make_user(client, admin_headers, "updaterole", role="viewer").json()
    r = client.patch(f"/users/{user['id']}", json={"role": "analyst"},
                     headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["role"] == "analyst"


# ── Delete (soft) ─────────────────────────────────────────────────────────────

def test_admin_can_deactivate_user(client, admin_headers):
    user = make_user(client, admin_headers, "deactivate").json()
    r = client.delete(f"/users/{user['id']}", headers=admin_headers)
    assert r.status_code == 200
    # Verify status changed to inactive
    updated = client.get(f"/users/{user['id']}", headers=admin_headers).json()
    assert updated["status"] == "inactive"


# ── RBAC ──────────────────────────────────────────────────────────────────────

def test_viewer_cannot_access_users(client, admin_headers):
    """Viewers must not be able to list or create users."""
    # Create viewer and login
    make_user(client, admin_headers, "viewer_rbac", role="viewer")
    token = client.post("/auth/login", data={
        "username": "test_viewer_rbac@example.com",
        "password": "TestPass1!",
    }).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/users/", headers=headers).status_code == 403
    assert client.post("/users/", json={}, headers=headers).status_code == 403
