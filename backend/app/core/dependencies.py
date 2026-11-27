"""Reusable FastAPI authentication and authorization dependencies."""
from __future__ import annotations

import logging

from fastapi import Cookie, Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.models.user import User
from app.services.token import TokenError, decode_access_token, is_token_revoked

logger = logging.getLogger("nigran360")

_bearer = HTTPBearer(auto_error=False)


def _http_401(message: str = "Authentication required") -> Exception:
    from fastapi import HTTPException
    return HTTPException(status_code=401, detail=message)


def _http_403(message: str = "Insufficient permissions") -> Exception:
    from fastapi import HTTPException
    return HTTPException(status_code=403, detail=message)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract and validate the Bearer access token; return the authenticated User."""
    if credentials is None:
        raise _http_401()

    try:
        payload = decode_access_token(credentials.credentials)
    except TokenError as exc:
        logger.info("Token decode failed: %s", exc)
        raise _http_401("Invalid or expired token") from exc

    jti = payload["jti"]
    if await is_token_revoked(db, jti):
        raise _http_401("Token has been revoked")

    user_id: str = payload["sub"]
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise _http_401("User not found")
    if not user.is_active:
        raise _http_403("Account is deactivated")

    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "administrator":
        raise _http_403()
    return current_user


async def require_examiner(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("administrator", "examiner"):
        raise _http_403()
    return current_user


async def require_candidate(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "candidate":
        raise _http_403()
    return current_user


def get_client_ip(x_real_ip: str | None = Header(None, alias="X-Real-IP")) -> str | None:
    """Return direct connection IP. Never trusts X-Forwarded-For."""
    return x_real_ip


# ---------------------------------------------------------------------------
# CSRF double-submit validation for cookie-authenticated endpoints
# ---------------------------------------------------------------------------

CSRF_HEADER = "X-CSRF-Token"
CSRF_COOKIE = "csrf_token"


def validate_csrf(
    csrf_header: str | None = Header(None, alias="X-CSRF-Token"),
    csrf_cookie: str | None = Cookie(None, alias="csrf_token"),
) -> None:
    """Validate CSRF double-submit for cookie-authenticated state-changing requests."""
    if not csrf_header or not csrf_cookie:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="CSRF validation failed")
    if csrf_header != csrf_cookie:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="CSRF token mismatch")
