"""
routers/record_routes.py
-------------------------
Financial record CRUD endpoints.

POST   /records           → create record        [Admin]
GET    /records           → list + filter + page  [All roles]
GET    /records/{id}      → single record         [All roles]
PUT    /records/{id}      → full/partial update   [Admin]
DELETE /records/{id}      → hard delete           [Admin]
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.core.role_checker import admin_only, any_authenticated
from app.models.user_model import User
from app.services import record_service
from app.schemas.record_schema import (
    RecordCreate, RecordUpdate, RecordOut, PaginatedRecords
)

router = APIRouter(prefix="/records", tags=["Financial Records"])


@router.post(
    "/",
    response_model=RecordOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a financial record  [Admin]",
)
def create_record(
    payload: RecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    """Admin adds a new income or expense record."""
    return record_service.create_record(db, payload, user_id=current_user.id)


@router.get(
    "/",
    response_model=PaginatedRecords,
    summary="List records with filters + pagination  [All roles]",
)
def list_records(
    page:        int            = Query(1,    ge=1,  description="Page number"),
    size:        int            = Query(20,   ge=1, le=100, description="Page size"),
    type:        Optional[str]  = Query(None, description="income | expense"),
    category:    Optional[str]  = Query(None, description="Category filter (partial match)"),
    date_from:   Optional[datetime] = Query(None, description="Start date  e.g. 2024-01-01T00:00:00"),
    date_to:     Optional[datetime] = Query(None, description="End date    e.g. 2024-12-31T23:59:59"),
    search:      Optional[str]  = Query(None, description="Search in category or notes"),
    db: Session = Depends(get_db),
    _: User     = Depends(any_authenticated),
):
    """
    Returns paginated records. Supports combined filters:
    - type, category, date range, free-text search
    """
    return record_service.get_records(
        db,
        page=page,
        size=size,
        record_type=type,
        category=category,
        date_from=date_from,
        date_to=date_to,
        search=search,
    )


@router.get(
    "/{record_id}",
    response_model=RecordOut,
    summary="Get a single record by ID  [All roles]",
)
def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User     = Depends(any_authenticated),
):
    return record_service.get_record_by_id(db, record_id)


@router.put(
    "/{record_id}",
    response_model=RecordOut,
    summary="Update a record  [Admin]",
)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    db: Session = Depends(get_db),
    _: User     = Depends(admin_only),
):
    return record_service.update_record(db, record_id, payload)


@router.delete(
    "/{record_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a record  [Admin]",
)
def delete_record(
    record_id: int,
    db: Session = Depends(get_db),
    _: User     = Depends(admin_only),
):
    return record_service.delete_record(db, record_id)
