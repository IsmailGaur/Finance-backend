# 💰 Finance Dashboard Backend

A production-ready REST API for managing financial records with **JWT authentication**, **role-based access control (RBAC)**, and **dashboard analytics**.

> **Submission Note:** This project fulfils all 6 core requirements of the Finance Data Processing and Access Control Backend assignment. See the [How This Matches the Assignment](#how-this-matches-the-assignment) section below.

---

## 🏗️ Project Structure

```
finance-backend/
├── app/
│   ├── main.py                   # App factory, startup, routers, CORS, error handlers
│   ├── database/
│   │   └── connection.py         # SQLAlchemy engine, session factory, Base, init_db()
│   ├── models/
│   │   ├── user_model.py         # User ORM model (id, name, email, role, status)
│   │   └── record_model.py       # FinancialRecord ORM model
│   ├── schemas/
│   │   ├── user_schema.py        # UserCreate, UserUpdate, UserOut, TokenResponse
│   │   ├── record_schema.py      # RecordCreate, RecordUpdate, RecordOut, Paginated
│   │   └── summary_schema.py     # DashboardSummary, CategoryTotal, MonthlyTrend, WeeklyTrend
│   ├── routers/
│   │   ├── auth_routes.py        # POST /auth/login, GET /auth/me
│   │   ├── user_routes.py        # CRUD /users  (admin only)
│   │   ├── record_routes.py      # CRUD /records (role-gated)
│   │   └── summary_routes.py     # GET /summary/* (analyst + admin)
│   ├── services/
│   │   ├── user_service.py       # User business logic + auth helper
│   │   ├── record_service.py     # Record CRUD + filtering + pagination
│   │   └── summary_service.py    # Dashboard aggregation: monthly, weekly, recent
│   └── core/
│       ├── config.py             # Pydantic Settings — reads from .env
│       ├── security.py           # JWT encode/decode, password hashing
│       ├── deps.py               # get_db, get_current_user FastAPI dependencies
│       └── role_checker.py       # require_roles(), admin_only, analyst_or_admin
├── tests/
│   ├── conftest.py               # In-memory SQLite fixtures (StaticPool)
│   ├── test_auth.py              # Auth endpoint tests
│   ├── test_users.py             # User CRUD + RBAC tests
│   ├── test_records.py           # Record CRUD + filter + pagination tests
│   └── test_summary.py          # Dashboard summary + RBAC tests
├── .env.example                  # Template for environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

| Layer          | Technology                                          |
|----------------|-----------------------------------------------------|
| Framework      | FastAPI 0.111 (ASGI, auto OpenAPI docs)             |
| ORM            | SQLAlchemy 2.0 (declarative models, sessions)       |
| Database       | SQLite (default) — swap `DATABASE_URL` for Postgres |
| Validation     | Pydantic v2 (schemas, field validators)             |
| Authentication | JWT via `python-jose`, password via `passlib`       |
| Server         | Uvicorn (ASGI)                                      |
| Testing        | Pytest + httpx + StaticPool in-memory DB            |

---

## 🚀 Setup & Running

### Prerequisites
- Python 3.10 or higher (`python --version` to check)

### 1. Extract the project
```bash
cd finance-backend
```

### 2. Create a virtual environment
```bash
# Mac / Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY for production
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

Server starts at **http://localhost:8000**

On first run, a default admin is automatically seeded:
```
Email:    admin@finance.com
Password: Admin1234!
```

### 6. View API documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:**       http://localhost:8000/redoc
- **Health:**      http://localhost:8000/health

---

## 🔐 Role-Based Access Control

| Role       | Permissions                                          |
|------------|------------------------------------------------------|
| `viewer`   | Read financial records only                          |
| `analyst`  | Read records + access all dashboard summary APIs     |
| `admin`    | Full CRUD on users and records + all summary APIs    |

RBAC is implemented using FastAPI dependency injection (`Depends()`). Each route declares its required roles in the function signature — no middleware, no manual checks inside handlers.

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint      | Access | Description             |
|--------|---------------|--------|-------------------------|
| POST   | `/auth/login` | Public | Login → JWT token       |
| GET    | `/auth/me`    | Any    | Current user profile    |

### User Management *(Admin only)*
| Method | Endpoint        | Description              |
|--------|-----------------|--------------------------|
| POST   | `/users/`       | Create user              |
| GET    | `/users/`       | List users (paginated)   |
| GET    | `/users/{id}`   | Get user by ID           |
| PATCH  | `/users/{id}`   | Partial update           |
| DELETE | `/users/{id}`   | Soft-delete (deactivate) |

### Financial Records
| Method | Endpoint          | Access     | Description                    |
|--------|-------------------|------------|--------------------------------|
| POST   | `/records/`       | Admin      | Create record                  |
| GET    | `/records/`       | All roles  | List + filter + paginate       |
| GET    | `/records/{id}`   | All roles  | Get single record              |
| PUT    | `/records/{id}`   | Admin      | Update record                  |
| DELETE | `/records/{id}`   | Admin      | Hard delete                    |

**GET /records/ query params:** `page`, `size`, `type` (income/expense), `category`, `date_from`, `date_to`, `search`

### Dashboard Summary *(Analyst + Admin)*
| Method | Endpoint                | Description                    |
|--------|-------------------------|--------------------------------|
| GET    | `/summary/`             | Full dashboard (all metrics)   |
| GET    | `/summary/income`       | Total income                   |
| GET    | `/summary/expense`      | Total expense                  |
| GET    | `/summary/balance`      | Net balance                    |
| GET    | `/summary/categories`   | Category-wise totals           |
| GET    | `/summary/trends`       | Monthly income/expense trends  |
| GET    | `/summary/weekly`       | Weekly income/expense trends   |
| GET    | `/summary/recent`       | Recent activity feed           |

---

## 🧪 Running Tests

```bash
pip install pytest httpx
pytest tests/ -v
```

Expected output: **45 passed**

Tests use an isolated in-memory SQLite database (via `StaticPool`) so they never touch `finance.db`.

---

## 📋 Example API Requests

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@finance.com&password=Admin1234!"
```

### Create a record
```bash
curl -X POST http://localhost:8000/records/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 5000, "type": "income", "category": "Salary", "date": "2024-06-01T00:00:00"}'
```

### Filter records
```bash
curl "http://localhost:8000/records/?type=expense&date_from=2024-01-01T00:00:00&page=1&size=10" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Full dashboard summary
```bash
curl http://localhost:8000/summary/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔍 How This Matches the Assignment

### Requirement 1 — User and Role Management
- **Users table:** `id`, `name`, `email`, `role`, `status`, `created_at`
- **Roles implemented:** `admin`, `analyst`, `viewer` with distinct permissions
- **User CRUD:** `POST /users/`, `GET /users/`, `PATCH /users/{id}`, `DELETE /users/{id}`
- **Status management:** Users can be activated/deactivated (soft-delete)
- **Files:** `models/user_model.py`, `schemas/user_schema.py`, `services/user_service.py`, `routers/user_routes.py`

### Requirement 2 — Financial Records Management
- **Record fields:** `amount`, `type` (income/expense), `category`, `date`, `notes`, `created_by`
- **Full CRUD:** create, read, update, delete operations
- **Filtering:** by type, category (partial match), date range, free-text search across category and notes
- **Pagination:** `page` + `size` query params on all list endpoints
- **Files:** `models/record_model.py`, `schemas/record_schema.py`, `services/record_service.py`, `routers/record_routes.py`

### Requirement 3 — Dashboard Summary APIs
- `GET /summary/` → total income, total expense, net balance, all breakdowns in one call
- `GET /summary/categories` → per-category income and expense totals with counts
- `GET /summary/trends` → monthly income/expense/net grouped by YYYY-MM
- `GET /summary/weekly` → weekly income/expense/net grouped by YYYY-Www
- `GET /summary/recent` → most recent N records (activity feed, N configurable via query param)
- **File:** `services/summary_service.py`, `routers/summary_routes.py`

### Requirement 4 — Access Control Logic
- **Implementation:** FastAPI dependency injection (`Depends()`) — RBAC declared in route signatures
- **Viewer:** read-only access to `/records/` endpoints only
- **Analyst:** read + all `/summary/` endpoints
- **Admin:** full access to `/users/` and `/records/` write operations
- **Enforcement:** 403 Forbidden returned with descriptive message when role insufficient
- **Files:** `core/role_checker.py`, `core/deps.py`

### Requirement 5 — Validation and Error Handling
- **Pydantic v2 schemas** with field constraints (amount > 0, min/max lengths, email validation)
- **Custom validators:** password strength (uppercase + digit required), category normalisation
- **HTTP status codes:** 200, 201, 400, 401, 403, 404, 409, 422, 500 used appropriately
- **Global exception handlers:** clean JSON error responses, no stack traces leaked to clients
- **Files:** `schemas/`, `main.py`

### Requirement 6 — Data Persistence
- **Database:** SQLite (file-based, zero setup) — swap one `.env` line for PostgreSQL
- **ORM:** SQLAlchemy 2.0 with declarative models, FK relationships, indexed columns
- **Auto-migration:** `Base.metadata.create_all()` on startup creates all tables
- **Assumption:** SQLite chosen for simplicity and portability; the `DATABASE_URL` setting makes PostgreSQL a one-line change

---

## 📝 Assumptions and Design Decisions

1. **SQLite over MongoDB** — The financial data is highly relational (users own records, FK constraints needed). SQLite gives zero-setup local development; PostgreSQL is one env-var away for production.

2. **Soft delete for users, hard delete for records** — Deleting a user while their financial records exist would violate FK integrity and lose audit history. Deactivating (status=inactive) preserves all data. Records have no dependents, so hard delete is safe.

3. **pbkdf2_sha256 for password hashing** — bcrypt has native C extension compatibility issues on Python 3.12 in some environments. pbkdf2_sha256 is NIST-approved, pure-Python, and zero-dependency.

4. **Analyst cannot create or modify records** — The assignment describes analyst as "view records and access insights." Write access was not mentioned and would conflict with the viewer/analyst/admin hierarchy.

5. **Category normalisation** — Categories are stored in Title Case (`"salary"` → `"Salary"`) to avoid duplicate categories from case differences.

6. **Amounts must be strictly positive** — Zero or negative amounts are rejected with 422. A zero-amount record has no financial meaning; negative values would reverse the income/expense polarity.

7. **JWT tokens expire in 60 minutes** — Configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`. No refresh token implemented (out of scope for assessment).

8. **Summary computed in Python, not SQL** — A single DB query fetches all rows; Python handles grouping. This keeps the code database-agnostic (SQLite's `strftime` differs from PostgreSQL's `date_trunc`). For 100,000+ records, push aggregation to SQL with `GROUP BY`.

9. **Auto-seeded admin on first startup** — Eliminates the chicken-and-egg problem of needing an admin to create the first admin. Seed runs only if no admin exists.

10. **CORS allows all origins** — Set to `"*"` for development. Lock down to specific frontend origins before production deployment.

---

## 🔄 Switching to PostgreSQL

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/finance_db

# Install driver
pip install psycopg2-binary
```

No other code changes needed.

---

## 🚢 Production Checklist

- [ ] Generate a new `SECRET_KEY` (`python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Set `DEBUG=False`
- [ ] Switch `DATABASE_URL` to PostgreSQL
- [ ] Restrict `CORS` origins to your frontend domain
- [ ] Change or remove the seeded admin credentials
- [ ] Put Nginx or a load balancer in front of Uvicorn
- [ ] Enable HTTPS

