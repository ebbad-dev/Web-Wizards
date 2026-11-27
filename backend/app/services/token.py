"""JWT creation, verification and revocation helpers."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings

_ACCESS_TYPE = "access"
_REFRESH_TYPE = "refresh"


# ---------------------------------------------------------------------------
# Token creation
# ---------------------------------------------------------------------------

def _now_utc() -> datetime:
    return datetime.now(UTC)


def create_access_token(user_id: str, role: str) -> tuple[str, str]:
    """Return (encoded_jwt, jti)."""
    jti = str(uuid.uuid4())
    expire = _now_utc() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {
        "sub": user_id,
        "role": role,
        "type": _ACCESS_TYPE,
        "jti": jti,
        "exp": expire,
        "iat": _now_utc(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM), jti


def create_refresh_token(user_id: str) -> tuple[str, str]:
    """Return (encoded_jwt, jti)."""
    jti = str(uuid.uuid4())
    expire = _now_utc() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload: dict[str, Any] = {
        "sub": user_id,
        "type": _REFRESH_TYPE,
        "jti": jti,
        "exp": expire,
        "iat": _now_utc(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM), jti


# ---------------------------------------------------------------------------
# Token verification
# ---------------------------------------------------------------------------

class TokenError(Exception):
    """Raised when a token is invalid, expired or revoked."""


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    """Decode and validate token claims. Raises TokenError on any failure."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise TokenError(f"Invalid token: {exc}") from exc

    if payload.get("type") != expected_type:
        raise TokenError(f"Expected token type '{expected_type}', got '{payload.get('type')}'")
    if "jti" not in payload:
        raise TokenError("Token missing jti claim")
    if "sub" not in payload:
        raise TokenError("Token missing sub claim")
    return payload


def decode_access_token(token: str) -> dict[str, Any]:
    return decode_token(token, _ACCESS_TYPE)


def decode_refresh_token(token: str) -> dict[str, Any]:
    return decode_token(token, _REFRESH_TYPE)


# ---------------------------------------------------------------------------
# DB-backed revocation
# ---------------------------------------------------------------------------

async def revoke_token(db: AsyncSession, jti: str, user_id: str, expires_at: datetime) -> None:
    """Insert a JTI into revoked_tokens. Import inline to avoid circular deps."""
    from app.models.session import RevokedToken
    row = RevokedToken(jti=jti, user_id=user_id, expires_at=expires_at)
    db.add(row)
    await db.commit()


async def is_token_revoked(db: AsyncSession, jti: str) -> bool:
    from app.models.session import RevokedToken
    result = await db.execute(select(RevokedToken).where(RevokedToken.jti == jti))
    return result.scalar_one_or_none() is not None
