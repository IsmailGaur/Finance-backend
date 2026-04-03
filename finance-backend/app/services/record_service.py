"""
services/record_service.py
---------------------------
Business logic for financial record CRUD + filtering + pagination.
"""

import math
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.record_model import FinancialRecord
from app.schemas.record_schema import RecordCreate, RecordUpdate, PaginatedRecords


# ── Create ────────────────────────────────────────────────────────────────────

def create_record(db: Session, payload: RecordCreate, user_id: int) -> FinancialRecord:
    """Insert a new financial record owned by `user_id`."""
    record = FinancialRecord(
        amount     = payload.amount,
        type       = payload.type,
        category   = payload.category,
        date       = payload.date,
        notes      = payload.notes,
        created_by = user_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# ── Read ──────────────────────────────────────────────────────────────────────

def get_records(
    db: Session,
    page: int = 1,
    size: int = 20,
    record_type: Optional[str] = None,
    category: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    search: Optional[str] = None,
) -> PaginatedRecords:
    """
    Return paginated records with optional filters:
      - record_type  : 'income' | 'expense'
      - category     : exact match (case-insensitive)
      - date_from/to : date range filter
      - search       : partial match on category or notes
    """
    query = db.query(FinancialRecord)

    # Build filter conditions
    filters = []
    if record_type:
        filters.append(FinancialRecord.type == record_type)
    if category:
        filters.append(FinancialRecord.category.ilike(f"%{category}%"))
    if date_from:
        filters.append(FinancialRecord.date >= date_from)
    if date_to:
        filters.append(FinancialRecord.date <= date_to)
    if search:
        filters.append(
            FinancialRecord.category.ilike(f"%{search}%")
            | FinancialRecord.notes.ilike(f"%{search}%")
        )

    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    records = (
        query
        .order_by(FinancialRecord.date.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    return PaginatedRecords(
        total   = total,
        page    = page,
        size    = size,
        pages   = math.ceil(total / size) if total else 0,
        records = records,
    )


def get_record_by_id(db: Session, record_id: int) -> FinancialRecord:
    """Fetch a single record or raise 404."""
    record = db.query(FinancialRecord).filter(FinancialRecord.id == record_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id={record_id} not found.",
        )
    return record


# ── Update ────────────────────────────────────────────────────────────────────

def update_record(db: Session, record_id: int, payload: RecordUpdate) -> FinancialRecord:
    """Apply partial updates to an existing record."""
    record = get_record_by_id(db, record_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)
    return record


# ── Delete ────────────────────────────────────────────────────────────────────

def delete_record(db: Session, record_id: int) -> dict:
    """Hard-delete a financial record."""
    record = get_record_by_id(db, record_id)
    db.delete(record)
    db.commit()
    return {"detail": f"Record id={record_id} deleted successfully."}
