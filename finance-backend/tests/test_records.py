"""
tests/test_records.py
----------------------
Tests for financial record CRUD, filtering, pagination,
and role-based access control.
"""

import pytest

VALID_RECORD = {
    "amount":   1500.00,
    "type":     "income",
    "category": "Salary",
    "date":     "2024-06-01T00:00:00",
    "notes":    "June salary",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def create_record(client, headers, overrides=None):
    data = {**VALID_RECORD, **(overrides or {})}
    return client.post("/records/", json=data, headers=headers)


# ── Create ────────────────────────────────────────────────────────────────────

def test_admin_can_create_record(client, admin_headers):
    r = create_record(client, admin_headers)
    assert r.status_code == 201
    body = r.json()
    assert body["amount"]   == 1500.00
    assert body["category"] == "Salary"   # auto-title-cased
    assert body["type"]     == "income"


def test_create_record_negative_amount_returns_422(client, admin_headers):
    r = create_record(client, admin_headers, {"amount": -100})
    assert r.status_code == 422


def test_create_record_zero_amount_returns_422(client, admin_headers):
    r = create_record(client, admin_headers, {"amount": 0})
    assert r.status_code == 422


def test_create_record_invalid_type_returns_422(client, admin_headers):
    r = create_record(client, admin_headers, {"type": "gift"})
    assert r.status_code == 422


def test_create_record_missing_required_fields(client, admin_headers):
    r = client.post("/records/", json={"amount": 100}, headers=admin_headers)
    assert r.status_code == 422


# ── Read ──────────────────────────────────────────────────────────────────────

def test_list_records_returns_paginated(client, admin_headers):
    r = client.get("/records/", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert "records" in body
    assert "total"   in body
    assert "page"    in body
    assert "pages"   in body


def test_filter_by_type_income(client, admin_headers):
    create_record(client, admin_headers, {"type": "expense", "category": "Rent"})
    r = client.get("/records/?type=income", headers=admin_headers)
    assert r.status_code == 200
    for rec in r.json()["records"]:
        assert rec["type"] == "income"


def test_filter_by_category(client, admin_headers):
    create_record(client, admin_headers, {"category": "Utilities"})
    r = client.get("/records/?category=utilities", headers=admin_headers)
    assert r.status_code == 200
    # At least one result should contain "Utilities"
    cats = [rec["category"] for rec in r.json()["records"]]
    assert any("Utilities" in c for c in cats)


def test_search_in_notes(client, admin_headers):
    create_record(client, admin_headers, {"notes": "UniqueSearchTerm99"})
    r = client.get("/records/?search=UniqueSearchTerm99", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["total"] >= 1


def test_pagination_size_respected(client, admin_headers):
    # Create 5 records
    for i in range(5):
        create_record(client, admin_headers, {"amount": float(100 + i)})
    r = client.get("/records/?page=1&size=2", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()["records"]) <= 2


def test_get_record_by_id(client, admin_headers):
    rec = create_record(client, admin_headers).json()
    r = client.get(f"/records/{rec['id']}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["id"] == rec["id"]


def test_get_nonexistent_record_returns_404(client, admin_headers):
    r = client.get("/records/999999", headers=admin_headers)
    assert r.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────

def test_admin_can_update_record(client, admin_headers):
    rec = create_record(client, admin_headers).json()
    r = client.put(f"/records/{rec['id']}",
                   json={"amount": 9999.99, "notes": "updated"},
                   headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["amount"] == 9999.99


# ── Delete ────────────────────────────────────────────────────────────────────

def test_admin_can_delete_record(client, admin_headers):
    rec = create_record(client, admin_headers).json()
    r = client.delete(f"/records/{rec['id']}", headers=admin_headers)
    assert r.status_code == 200
    assert client.get(f"/records/{rec['id']}",
                      headers=admin_headers).status_code == 404


# ── RBAC ──────────────────────────────────────────────────────────────────────

def test_viewer_can_read_records(client, admin_headers):
    """Viewers have read-only access to records."""
    client.post("/users/", json={
        "name": "RViewer", "email": "rviewer@test.com",
        "password": "ViewR1pass!", "role": "viewer", "status": "active",
    }, headers=admin_headers)
    token = client.post("/auth/login", data={
        "username": "rviewer@test.com", "password": "ViewR1pass!",
    }).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    assert client.get("/records/", headers=h).status_code == 200


def test_viewer_cannot_create_record(client, admin_headers):
    """Viewers must be blocked from creating records."""
    token = client.post("/auth/login", data={
        "username": "rviewer@test.com", "password": "ViewR1pass!",
    }).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    assert create_record(client, h).status_code == 403


def test_unauthenticated_cannot_read_records(client):
    r = client.get("/records/")
    assert r.status_code == 401
