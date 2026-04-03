"""
tests/test_summary.py
----------------------
Tests for all dashboard summary endpoints and RBAC enforcement.
"""

RECORD_INCOME  = {"amount": 5000, "type": "income",  "category": "Salary",
                  "date": "2024-06-01T00:00:00", "notes": "June"}
RECORD_EXPENSE = {"amount": 1200, "type": "expense", "category": "Rent",
                  "date": "2024-06-05T00:00:00", "notes": "rent"}


def seed_records(client, headers):
    client.post("/records/", json=RECORD_INCOME,  headers=headers)
    client.post("/records/", json=RECORD_EXPENSE, headers=headers)


# ── Access control ────────────────────────────────────────────────────────────

def test_viewer_blocked_from_full_summary(client, admin_headers):
    """Viewers must not access /summary/ — 403 expected."""
    client.post("/users/", json={
        "name": "SViewer", "email": "sviewer@test.com",
        "password": "ViewS1pass!", "role": "viewer", "status": "active",
    }, headers=admin_headers)
    token = client.post("/auth/login", data={
        "username": "sviewer@test.com", "password": "ViewS1pass!",
    }).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    assert client.get("/summary/",           headers=h).status_code == 403
    assert client.get("/summary/income",     headers=h).status_code == 403
    assert client.get("/summary/balance",    headers=h).status_code == 403
    assert client.get("/summary/categories", headers=h).status_code == 403
    assert client.get("/summary/trends",     headers=h).status_code == 403
    assert client.get("/summary/weekly",     headers=h).status_code == 403
    assert client.get("/summary/recent",     headers=h).status_code == 403


def test_analyst_can_access_summary(client, admin_headers):
    """Analysts must have read access to all summary endpoints."""
    client.post("/users/", json={
        "name": "Analyst1", "email": "analyst1@test.com",
        "password": "Analyst1pass!", "role": "analyst", "status": "active",
    }, headers=admin_headers)
    token = client.post("/auth/login", data={
        "username": "analyst1@test.com", "password": "Analyst1pass!",
    }).json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    assert client.get("/summary/", headers=h).status_code == 200


def test_unauthenticated_cannot_access_summary(client):
    assert client.get("/summary/").status_code == 401


# ── Data correctness ──────────────────────────────────────────────────────────

def test_summary_totals_correct(client, admin_headers):
    seed_records(client, admin_headers)
    r = client.get("/summary/", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()

    # totals must be non-negative numbers
    assert body["total_income"]  >= 0
    assert body["total_expense"] >= 0
    # net = income - expense
    assert abs(body["net_balance"] -
               (body["total_income"] - body["total_expense"])) < 0.01
    assert body["record_count"] >= 2


def test_summary_has_required_fields(client, admin_headers):
    r = client.get("/summary/", headers=admin_headers)
    body = r.json()
    required = [
        "total_income", "total_expense", "net_balance",
        "record_count", "category_totals", "monthly_trends",
        "weekly_trends", "recent_activity",
    ]
    for field in required:
        assert field in body, f"Missing field: {field}"


def test_category_totals_structure(client, admin_headers):
    r = client.get("/summary/categories", headers=admin_headers)
    assert r.status_code == 200
    cats = r.json()
    assert isinstance(cats, list)
    if cats:
        assert "category"      in cats[0]
        assert "total"         in cats[0]
        assert "income_total"  in cats[0]
        assert "expense_total" in cats[0]
        assert "count"         in cats[0]


def test_monthly_trends_structure(client, admin_headers):
    r = client.get("/summary/trends", headers=admin_headers)
    assert r.status_code == 200
    trends = r.json()
    if trends:
        assert "month"   in trends[0]
        assert "income"  in trends[0]
        assert "expense" in trends[0]
        assert "net"     in trends[0]


def test_weekly_trends_endpoint(client, admin_headers):
    r = client.get("/summary/weekly", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_recent_activity_returns_list(client, admin_headers):
    r = client.get("/summary/recent", headers=admin_headers)
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_recent_activity_limit_param(client, admin_headers):
    r = client.get("/summary/recent?limit=3", headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()) <= 3


def test_balance_endpoint(client, admin_headers):
    r = client.get("/summary/balance", headers=admin_headers)
    assert r.status_code == 200
    body = r.json()
    assert "net_balance"   in body
    assert "total_income"  in body
    assert "total_expense" in body
