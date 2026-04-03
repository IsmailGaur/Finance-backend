"""
core/deps.py
------------
Shared FastAPI dependencies.

Provides:
  - get_db          → yields a SQLAlchemy session per request
  - get_current_user → decodes JWT and returns the matching DB user
  - get_current_active_user → additionally enforces 'active' status
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.core.security import decode_access_token
from app.models.user_model import User

# Tells FastAPI where the login endpoint lives (used in Swagger UI)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ── Database session ──────────────────────────────────────────────────────────

def get_db():
    """
    Yield a database session and guarantee it is closed after the request,
    even if an exception is raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Current user ──────────────────────────────────────────────────────────────

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the Bearer token, look up the user in the DB, and return them.
    Raises 401 if the token is invalid or the user no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Extend get_current_user to additionally reject inactive accounts.
    Raises 403 if the user's status is not 'active'.
    """
    if current_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact an administrator.",
        )
    return current_user
