"""Integration tests for /api/v1/auth/* endpoints."""
from __future__ import annotations

from datetime import UTC

import pytest

_REGISTER_URL = "/api/v1/auth/register"
_LOGIN_URL = "/api/v1/auth/login"
_ME_URL = "/api/v1/auth/me"
_LOGOUT_URL = "/api/v1/auth/logout"
_REFRESH_URL = "/api/v1/auth/refresh"

CANDIDATE = {"email": "candidate@test.com", "full_name": "Test Candidate", "password": "Password1!"}


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_register_success(client):
    r = await client.post(_REGISTER_URL, json=CANDIDATE)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == CANDIDATE["email"]
    assert data["role"] == "candidate"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post(_REGISTER_URL, json=CANDIDATE)
    r = await client.post(_REGISTER_URL, json=CANDIDATE)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_register_role_hardcoded_to_candidate(client):
    payload = {**CANDIDATE, "email": "hacker@test.com", "role": "administrator"}
    r = await client.post(_REGISTER_URL, json=payload)
    # Field not in RegisterRequest schema — should still register as candidate
    assert r.status_code == 201
    assert r.json()["role"] == "candidate"


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post(_REGISTER_URL, json=CANDIDATE)
    r = await client.post(_LOGIN_URL, json={"email": CANDIDATE["email"], "password": CANDIDATE["password"]})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert "user" in body
    assert body["user"]["email"] == CANDIDATE["email"]
    # Refresh cookie must be HttpOnly — not visible in Set-Cookie value
    cookies = r.headers.get_list("set-cookie")
    refresh_cookie = next((c for c in cookies if "refresh_token" in c), None)
    assert refresh_cookie is not None
    assert "HttpOnly" in refresh_cookie


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post(_REGISTER_URL, json=CANDIDATE)
    r = await client.post(_LOGIN_URL, json={"email": CANDIDATE["email"], "password": "WrongPass1!"})
    assert r.status_code == 401
    # Must not reveal account existence
    assert "Invalid credentials" in r.json()["message"]


@pytest.mark.asyncio
async def test_login_unknown_email(client):
    r = await client.post(_LOGIN_URL, json={"email": "nobody@test.com", "password": "SomePass1!"})
    assert r.status_code == 401
    assert "Invalid credentials" in r.json()["message"]


@pytest.mark.asyncio
async def test_login_rate_limit(client):
    await client.post(_REGISTER_URL, json=CANDIDATE)
    for _ in range(10):
        await client.post(_LOGIN_URL, json={"email": CANDIDATE["email"], "password": "wrong"})
    r = await client.post(_LOGIN_URL, json={"email": CANDIDATE["email"], "password": "wrong"})
    assert r.status_code == 429


# ---------------------------------------------------------------------------
# /auth/me
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_me_authenticated(client):
    await client.post(_REGISTER_URL, json=CANDIDATE)
    login_r = await client.post(_LOGIN_URL, json={"email": CANDIDATE["email"], "password": CANDIDATE["password"]})
    token = login_r.json()["access_token"]
    r = await client.get(_ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == CANDIDATE["email"]


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    r = await client.get(_ME_URL)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_me_invalid_token(client):
    r = await client.get(_ME_URL, headers={"Authorization": "Bearer notavalidtoken"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# /auth/logout
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_logout_revokes_access_token(client):
    await client.post(_REGISTER_URL, json=CANDIDATE)
    login_r = await client.post(_LOGIN_URL, json={"email": CANDIDATE["email"], "password": CANDIDATE["password"]})
    token = login_r.json()["access_token"]
    csrf = login_r.cookies.get("csrf_token", "dummy-csrf")

    # Logout
    await client.post(
        _LOGOUT_URL,
        headers={"Authorization": f"Bearer {token}", "X-CSRF-Token": csrf},
    )

    # Access token must be revoked
    r = await client.get(_ME_URL, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


# ---------------------------------------------------------------------------
# /auth/refresh
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_refresh_issues_new_access_token(client):
    await client.post(_REGISTER_URL, json=CANDIDATE)
    login_r = await client.post(_LOGIN_URL, json={"email": CANDIDATE["email"], "password": CANDIDATE["password"]})
    csrf = login_r.cookies.get("csrf_token", "dummy-csrf")

    r = await client.post(_REFRESH_URL, headers={"X-CSRF-Token": csrf})
    assert r.status_code == 200
    assert "access_token" in r.json()


@pytest.mark.asyncio
async def test_refresh_without_cookie_returns_4xx(client):
    # No cookies at all: CSRF check fires first (403), or if bypassed, refresh returns 401.
    r = await client.post(_REFRESH_URL, headers={"X-CSRF-Token": "some-csrf"})
    assert r.status_code in (401, 403)


@pytest.mark.asyncio
async def test_refresh_rotation_prevents_reuse(client, db_session):
    """After a successful refresh, the old refresh token is revoked in the DB.
    Simulated by calling is_token_revoked directly after rotation."""
    from datetime import datetime

    from app.services.token import (
        create_refresh_token,
        decode_refresh_token,
        is_token_revoked,
        revoke_token,
    )

    user_id = "00000000-0000-0000-0000-000000000001"
    old_token, old_jti = create_refresh_token(user_id)
    payload = decode_refresh_token(old_token)
    expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)

    # Revoke the old token (simulating what /refresh does)
    await revoke_token(db_session, old_jti, user_id, expires_at)

    # Verify it's now revoked
    assert await is_token_revoked(db_session, old_jti) is True

    # A new token from the same user should NOT be revoked
    _, new_jti = create_refresh_token(user_id)
    assert await is_token_revoked(db_session, new_jti) is False
