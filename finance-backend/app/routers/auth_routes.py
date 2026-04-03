"""
routers/auth_routes.py
-----------------------
Authentication endpoints.

POST /auth/login   → receive credentials, return JWT token
POST /auth/me      → return the currently authenticated user
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_active_user
from app.core.security import create_access_token
from app.services.user_service import authenticate_user
from app.schemas.user_schema import TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive a JWT token",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Accepts `username` (which is the email) and `password` as form fields.
    Returns a Bearer token valid for `ACCESS_TOKEN_EXPIRE_MINUTES` minutes.
    """
    # OAuth2PasswordRequestForm uses 'username' field by convention
    user  = authenticate_user(db, form_data.username, form_data.password)
    token = create_access_token({"sub": user.email})
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the currently authenticated user",
)
def me(current_user=Depends(get_current_active_user)):
    """Returns profile of the bearer token owner."""
    return current_user
