"""
core/role_checker.py
---------------------
Dependency factories for role-based access control (RBAC).
Inject these into route handlers to enforce permissions declaratively.

Role hierarchy:
  viewer  → read-only access
  analyst → read + summary access
  admin   → full access (create / update / delete)
"""

from typing import List
from fastapi import Depends, HTTPException, status

from app.core.deps import get_current_active_user
from app.models.user_model import User


def require_roles(allowed_roles: List[str]):
    """
    Returns a FastAPI dependency that raises 403 if the
    authenticated user's role is not in `allowed_roles`.

    Usage:
        @router.post("/records", dependencies=[Depends(require_roles(["admin"]))])
    """
    def _checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}. "
                       f"Your role: '{current_user.role}'.",
            )
        return current_user
    return _checker


# ── Convenience role dependencies ─────────────────────────────────────────────

def admin_only(current_user: User = Depends(require_roles(["admin"]))) -> User:
    """Restrict endpoint to admins only."""
    return current_user


def analyst_or_admin(
    current_user: User = Depends(require_roles(["analyst", "admin"]))
) -> User:
    """Restrict endpoint to analysts and admins."""
    return current_user


def any_authenticated(
    current_user: User = Depends(require_roles(["viewer", "analyst", "admin"]))
) -> User:
    """Allow any authenticated and active user."""
    return current_user
