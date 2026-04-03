"""
main.py
-------
FastAPI application entry point.

Responsibilities:
  - Create the FastAPI app with metadata
  - Register all routers
  - Initialise the database on startup
  - Mount global exception handlers
  - Configure CORS (adjust origins for production)
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.config import get_settings
from app.database.connection import init_db
from app.routers import auth_routes, user_routes, record_routes, summary_routes

settings = get_settings()

# ── App factory ───────────────────────────────────────────────────────────────

app = FastAPI(
    title       = settings.app_name,
    version     = settings.app_version,
    description = (
        "## Finance Dashboard Backend\n\n"
        "A role-based REST API for managing financial records and generating "
        "dashboard summaries.\n\n"
        "### Roles\n"
        "| Role     | Permissions                         |\n"
        "|----------|-------------------------------------|\n"
        "| viewer   | Read financial records              |\n"
        "| analyst  | Read + access dashboard summaries   |\n"
        "| admin    | Full CRUD on users and records      |\n\n"
        "### Quick Start\n"
        "1. `POST /auth/login` with the seeded admin credentials\n"
        "2. Copy the returned `access_token`\n"
        "3. Click **Authorize** (🔒) above and paste `Bearer <token>`\n"
    ),
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],       # Lock down to specific origins in production
    allow_methods  = ["*"],
    allow_headers  = ["*"],
    allow_credentials = True,
)

# ── Global exception handlers ─────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return a clean 422 response with all validation errors listed."""
    errors = [
        {"field": ".".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all handler – prevents stack traces leaking to clients."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )

# ── Startup event ─────────────────────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    """Create all DB tables and seed an initial admin user if none exists."""
    init_db()
    _seed_admin()


def _seed_admin():
    """
    Insert a default admin user on first run so the API is immediately usable.
    Credentials: admin@finance.com / Admin1234!
    """
    from app.database.connection import SessionLocal
    from app.models.user_model import User
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == "admin@finance.com").first():
            db.add(User(
                name     = "Super Admin",
                email    = "admin@finance.com",
                password = hash_password("Admin1234!"),
                role     = "admin",
                status   = "active",
            ))
            db.commit()
            print("✅  Seeded default admin → admin@finance.com / Admin1234!")
    finally:
        db.close()

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(record_routes.router)
app.include_router(summary_routes.router)

# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"], summary="API health check")
def health():
    return {
        "status":  "ok",
        "app":     settings.app_name,
        "version": settings.app_version,
    }
