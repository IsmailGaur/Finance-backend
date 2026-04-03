# 🚀 How to Run — Finance Dashboard (Full Stack)

## Files in this package
- `finance-backend/` — FastAPI Python backend (port 8000)
- `finance-frontend/` — Single HTML file frontend (open in browser)

---

## Step 1 — Start the Backend

```bash
# Enter backend folder
cd finance-backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Start the server
uvicorn app.main:app --reload
```

Server starts at **http://localhost:8000**

On first run, a default admin is automatically created:
```
Email:    admin@finance.com
Password: Admin1234!
```

---

## Step 2 — Open the Frontend

**Option A (easiest):** Just double-click `finance-frontend/index.html`

**Option B (recommended):** Serve it locally to avoid any browser CORS issues:
```bash
cd finance-frontend
python3 -m http.server 3000
# Then open http://localhost:3000
```

---

## Step 3 — Login and Use

1. Open the frontend in your browser
2. Login with `admin@finance.com` / `Admin1234!`
3. You'll see the full dashboard

---

## What each page does

| Page | Role required | Description |
|------|--------------|-------------|
| Dashboard | Analyst + Admin | Summary stats, monthly chart, recent activity, category breakdown |
| Records | All (admin to edit) | List, filter, search, add/edit/delete financial records |
| Analytics | Analyst + Admin | Weekly trends chart, monthly breakdown table |
| Users | Admin only | Create, edit, activate/deactivate users |

---

## API Documentation (backend)
- Swagger UI: http://localhost:8000/docs
- ReDoc:       http://localhost:8000/redoc

---

## Running Tests (backend)
```bash
cd finance-backend
pip install pytest httpx
pytest tests/ -v
# Expected: 45 passed
```

---

## Troubleshooting

**"Failed to fetch" in browser:** Make sure the backend is running at http://localhost:8000

**"CORS error":** Use Option B (python http.server) instead of double-clicking the file

**"45 tests passed" but API fails:** The `.env` file must exist — copy from `.env.example`
