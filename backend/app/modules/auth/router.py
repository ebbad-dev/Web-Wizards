"""Authentication endpoints: login, register, logout, me, refresh."""
from __future__ import annotations

import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Cookie, Depends, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, validate_csrf
from app.core.rate_limit import check_login_rate_limit
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, RegisterRequest, TokenResponse, UserPublic
from app.services.password import hash_password, needs_rehash, verify_password
from app.services.token import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    is_token_revoked,
    revoke_token,
)

logger = logging.getLogger("nigran360")
router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE = "refresh_token"
_CSRF_COOKIE = "csrf_token"
_COOKIE_PATH = "/api/v1/auth"


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _set_refresh_cookie(response: Response, token: str, is_production: bool = False) -> None:
    expire = _now_utc() + timedelta(days=7)
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=token,
        httponly=True,
        secure=is_production,
        samesite="lax",
        path=_COOKIE_PATH,
        expires=int(expire.timestamp()),
    )


def _set_csrf_cookie(response: Response, csrf_value: str, is_production: bool = False) -> None:
    expire = _now_utc() + timedelta(days=7)
    response.set_cookie(
        key=_CSRF_COOKIE,
        value=csrf_value,
        httponly=False,
        secure=is_production,
        samesite="strict",
        path=_COOKIE_PATH,
        expires=int(expire.timestamp()),
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(_REFRESH_COOKIE, path=_COOKIE_PATH)
    response.delete_cookie(_CSRF_COOKIE, path=_COOKIE_PATH)


def _is_production() -> bool:
    from app.core.config import settings
    return settings.ENVIRONMENT == "production"


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

@router.post("/login", response_model=LoginResponse)
async def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    client_ip = request.client.host if request.client else None

    if not check_login_rate_limit(client_ip):
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail="Too many login attempts. Try again later.")

    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    # Generic message — do not reveal whether the email exists.
    if user is None or not verify_password(body.password, user.hashed_password):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Account is deactivated")

    # Rehash if Argon2 parameters changed.
    if needs_rehash(user.hashed_password):
        user.hashed_password = hash_password(body.password)

    # Record last login.
    user.last_login_at = _now_utc()
    await db.commit()
    await db.refresh(user)

    access_token, _access_jti = create_access_token(user.id, user.role)
    refresh_token, _refresh_jti = create_refresh_token(user.id)
    csrf_value = secrets.token_hex(32)

    production = _is_production()
    _set_refresh_cookie(response, refresh_token, is_production=production)
    _set_csrf_cookie(response, csrf_value, is_production=production)

    logger.info("User %s logged in", user.id)
    return LoginResponse(
        access_token=access_token,
        user=UserPublic.model_validate(user),
    )


# ---------------------------------------------------------------------------
# POST /auth/register (candidate self-registration)
# ---------------------------------------------------------------------------

@router.post("/register", response_model=UserPublic, status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserPublic:
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none() is not None:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=body.email,
        full_name=body.full_name,
        hashed_password=hash_password(body.password),
        role="candidate",  # Always candidate — backend enforced, never client-supplied.
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info("New candidate registered: %s", user.id)
    return UserPublic.model_validate(user)


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserPublic)
async def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.model_validate(current_user)


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------

@router.post("/logout", status_code=204)
async def logout(
    response: Response,
    request: Request,
    current_user: User = Depends(get_current_user),
    _csrf: None = Depends(validate_csrf),
    refresh_token: str | None = Cookie(None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db),
) -> None:

    # Revoke the access token jti from the Authorization header.
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        raw = auth_header[7:]
        try:
            from app.services.token import decode_access_token
            payload = decode_access_token(raw)
            expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
            await revoke_token(db, payload["jti"], current_user.id, expires_at)
        except TokenError:
            pass

    # Revoke the refresh token.
    if refresh_token:
        try:
            from app.services.token import decode_refresh_token
            payload = decode_refresh_token(refresh_token)
            expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
            await revoke_token(db, payload["jti"], current_user.id, expires_at)
        except TokenError:
            pass

    _clear_auth_cookies(response)
    logger.info("User %s logged out", current_user.id)


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    _csrf: None = Depends(validate_csrf),
    refresh_token: str | None = Cookie(None, alias="refresh_token"),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    from fastapi import HTTPException

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = decode_refresh_token(refresh_token)
    except TokenError as exc:
        _clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc

    jti = payload["jti"]
    if await is_token_revoked(db, jti):
        # Possible token reuse — clear cookies.
        _clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail="Refresh token has been revoked")

    user_id: str = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        _clear_auth_cookies(response)
        raise HTTPException(status_code=401, detail="User unavailable")

    # Rotation: revoke old refresh token before issuing a new one.
    old_expires = datetime.fromtimestamp(payload["exp"], tz=UTC)
    await revoke_token(db, jti, user_id, old_expires)

    new_access, _access_jti = create_access_token(user.id, user.role)
    new_refresh, _refresh_jti = create_refresh_token(user.id)
    csrf_value = secrets.token_hex(32)

    production = _is_production()
    _set_refresh_cookie(response, new_refresh, is_production=production)
    _set_csrf_cookie(response, csrf_value, is_production=production)

    return TokenResponse(access_token=new_access)
