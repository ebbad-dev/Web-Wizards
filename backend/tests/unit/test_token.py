"""Unit tests for JWT token service."""
from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.token import (
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    is_token_revoked,
)


def test_access_token_roundtrip():
    user_id = str(uuid.uuid4())
    token, jti = create_access_token(user_id, "candidate")
    payload = decode_access_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == "candidate"
    assert payload["type"] == "access"
    assert payload["jti"] == jti


def test_refresh_token_roundtrip():
    user_id = str(uuid.uuid4())
    token, jti = create_refresh_token(user_id)
    payload = decode_refresh_token(token)
    assert payload["sub"] == user_id
    assert payload["type"] == "refresh"
    assert payload["jti"] == jti


def test_access_token_wrong_type_rejected():
    user_id = str(uuid.uuid4())
    # Pass a refresh token to decode_access_token — must raise
    token, _ = create_refresh_token(user_id)
    with pytest.raises(TokenError):
        decode_access_token(token)


def test_refresh_token_wrong_type_rejected():
    user_id = str(uuid.uuid4())
    token, _ = create_access_token(user_id, "candidate")
    with pytest.raises(TokenError):
        decode_refresh_token(token)


def test_tampered_token_rejected():
    user_id = str(uuid.uuid4())
    token, _ = create_access_token(user_id, "candidate")
    tampered = token[:-4] + "XXXX"
    with pytest.raises(TokenError):
        decode_access_token(tampered)


def test_jti_is_unique():
    uid = str(uuid.uuid4())
    _, jti1 = create_access_token(uid, "candidate")
    _, jti2 = create_access_token(uid, "candidate")
    assert jti1 != jti2


@pytest.mark.asyncio
async def test_is_token_revoked_false_when_no_row():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    assert await is_token_revoked(mock_db, "some-jti") is False


@pytest.mark.asyncio
async def test_is_token_revoked_true_when_row_exists():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = object()  # any truthy value
    mock_db.execute.return_value = mock_result

    assert await is_token_revoked(mock_db, "some-jti") is True
