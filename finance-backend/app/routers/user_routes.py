"""
routers/user_routes.py
-----------------------
User management endpoints – Admin access only.

POST   /users           → create user
GET    /users           → list all users (with filters + pagination)
GET    /users/{id}      → get single user
PATCH  /users/{id}      → partial update
DELETE /users/{id}      → soft-delete (deactivate)
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.role_checker import admin_only
from app.services import user_service
from app.schemas.user_schema import UserCreate, UserUpdate, UserOut

router = APIRouter(prefix="/users", tags=["User Management"])


@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user  [Admin]",
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    _: object = Depends(admin_only),          # enforces admin role
):
    """Admin creates a user and assigns a role."""
    return user_service.create_user(db, payload)


@router.get(
    "/",
    response_model=List[UserOut],
    summary="List all users  [Admin]",
)
def list_users(
    skip:   int           = Query(0,  ge=0,  description="Records to skip"),
    limit:  int           = Query(20, ge=1, le=100, description="Page size"),
    role:   Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    _: object   = Depends(admin_only),
):
    """Paginated list of users. Optionally filter by role or status."""
    return user_service.get_all_users(db, skip=skip, limit=limit, role=role, status=status)


@router.get(
    "/{user_id}",
    response_model=UserOut,
    summary="Get a user by ID  [Admin]",
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: object   = Depends(admin_only),
):
    return user_service.get_user_by_id(db, user_id)


@router.patch(
    "/{user_id}",
    response_model=UserOut,
    summary="Update user fields  [Admin]",
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    _: object   = Depends(admin_only),
):
    """Partial update – only provided fields are changed."""
    return user_service.update_user(db, user_id, payload)


@router.delete(
    "/{user_id}",
    summary="Deactivate a user  [Admin]",
    status_code=status.HTTP_200_OK,
)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: object   = Depends(admin_only),
):
    """Soft-delete: sets status to 'inactive'. Preserves financial records."""
    return user_service.delete_user(db, user_id)
