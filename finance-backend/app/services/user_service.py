"""
services/user_service.py
-------------------------
Business logic for user management.
All DB operations are contained here; routes stay thin.
"""

from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password


# ── Create ────────────────────────────────────────────────────────────────────

def create_user(db: Session, payload: UserCreate) -> User:
    """
    Create a new user.
    Raises 409 if the email is already registered.
    """
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Email '{payload.email}' is already registered.",
        )

    user = User(
        name     = payload.name,
        email    = payload.email,
        password = hash_password(payload.password),
        role     = payload.role,
        status   = payload.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ── Read ──────────────────────────────────────────────────────────────────────

def get_all_users(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    role: Optional[str] = None,
    status: Optional[str] = None,
) -> List[User]:
    """Return a paginated, optionally filtered list of users."""
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    return query.offset(skip).limit(limit).all()


def get_user_by_id(db: Session, user_id: int) -> User:
    """Fetch a single user or raise 404."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id={user_id} not found.",
        )
    return user


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Return user by email or None."""
    return db.query(User).filter(User.email == email).first()


# ── Update ────────────────────────────────────────────────────────────────────

def update_user(db: Session, user_id: int, payload: UserUpdate) -> User:
    """
    Partial update – only provided fields are changed.
    Hashes password if a new one is supplied.
    """
    user = get_user_by_id(db, user_id)

    update_data = payload.model_dump(exclude_unset=True)

    # Hash new password if provided
    if "password" in update_data:
        update_data["password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


# ── Delete (soft) ─────────────────────────────────────────────────────────────

def delete_user(db: Session, user_id: int) -> dict:
    """
    Soft-delete: set status to 'inactive' rather than removing the row.
    This preserves financial records integrity.
    """
    user = get_user_by_id(db, user_id)
    user.status = "inactive"
    db.commit()
    return {"detail": f"User id={user_id} deactivated successfully."}


# ── Auth helper ───────────────────────────────────────────────────────────────

def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Validate credentials and return the user.
    Raises 401 on invalid email or wrong password.
    """
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status == "inactive":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact an administrator.",
        )
    return user
