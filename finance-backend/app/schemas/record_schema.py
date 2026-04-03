"""
schemas/record_schema.py
-------------------------
Pydantic v2 schemas for financial record validation and serialisation.

RecordCreate  → POST body
RecordUpdate  → PUT body (all fields optional)
RecordOut     → response shape
RecordFilter  → query param model for filtering/search
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


# ── Shared fields ─────────────────────────────────────────────────────────────

class RecordBase(BaseModel):
    amount:   float  = Field(..., gt=0, examples=[1500.00],
                             description="Transaction amount – must be positive.")
    type:     Literal["income", "expense"] = Field(..., examples=["income"])
    category: str    = Field(..., min_length=2, max_length=100, examples=["Salary"])
    date:     datetime = Field(..., examples=["2024-06-15T00:00:00"])
    notes:    Optional[str] = Field(None, max_length=500, examples=["June salary"])

    @field_validator("category")
    @classmethod
    def category_strip(cls, v: str) -> str:
        return v.strip().title()


# ── Request schemas ───────────────────────────────────────────────────────────

class RecordCreate(RecordBase):
    """Used by admin/analyst to create a new record (POST /records)."""
    pass


class RecordUpdate(BaseModel):
    """All fields optional for PUT /records/{id}."""
    amount:   Optional[float]   = Field(None, gt=0)
    type:     Optional[Literal["income", "expense"]] = None
    category: Optional[str]     = Field(None, min_length=2, max_length=100)
    date:     Optional[datetime] = None
    notes:    Optional[str]      = Field(None, max_length=500)


# ── Response schema ───────────────────────────────────────────────────────────

class RecordOut(RecordBase):
    id:         int
    created_by: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Pagination schema ─────────────────────────────────────────────────────────

class PaginatedRecords(BaseModel):
    total:   int
    page:    int
    size:    int
    pages:   int
    records: list[RecordOut]
