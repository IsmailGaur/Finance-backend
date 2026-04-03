"""
schemas/user_schema.py
-----------------------
Pydantic v2 schemas for request validation and response serialisation.

Naming convention:
  UserCreate  → POST body (includes plain-text password)
  UserUpdate  → PATCH body (all fields optional)
  UserOut     → response (password excluded)
  UserInDB    → internal representation (includes hashed password)
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Shared fields ─────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    name:  str      = Field(..., min_length=2, max_length=100, examples=["Alice Smith"])
    email: EmailStr = Field(..., examples=["alice@example.com"])
    role:  Literal["admin", "analyst", "viewer"] = Field(default="viewer")
    status: Literal["active", "inactive"] = Field(default="active")


# ── Request schemas ───────────────────────────────────────────────────────────

class UserCreate(UserBase):
    """Used when an admin creates a new user (POST /users)."""
    password: str = Field(..., min_length=8, examples=["SecurePass1!"])

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


class UserUpdate(BaseModel):
    """All fields are optional for PATCH /users/{id}."""
    name:   Optional[str]                              = Field(None, min_length=2, max_length=100)
    email:  Optional[EmailStr]                         = None
    role:   Optional[Literal["admin", "analyst", "viewer"]] = None
    status: Optional[Literal["active", "inactive"]]   = None
    password: Optional[str]                            = Field(None, min_length=8)


# ── Response schemas ──────────────────────────────────────────────────────────

class UserOut(UserBase):
    """Returned in API responses – never exposes the password."""
    id:         int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Auth schemas ──────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user:         UserOut
