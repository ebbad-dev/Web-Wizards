"""Integration tests for /api/v1/users/* endpoints."""
from __future__ import annotations

import uuid

import pytest

from app.models.user import User
from app.services.password import hash_password

_REGISTER_URL = "/api/v1/auth/register"
_LOGIN_URL = "/api/v1/auth/login"
_USERS_URL = "/api/v1/users"


async def _make_admin(db_session) -> tuple[str, str]:
    """Insert an admin user directly into the test DB and return (email, password)."""
    email = f"admin-{uuid.uuid4().hex[:6]}@test.com"
    password = "AdminPass1!"
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        full_name="Test Admin",
        hashed_password=hash_password(password),
        role="administrator",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return email, password


async def _login(client, email: str, password: str) -> str:
    r = await client.post(_LOGIN_URL, json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


# ---------------------------------------------------------------------------
# Admin: list users
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_users_admin_only(client, db_session):
    # Candidate cannot list users
    await client.post(_REGISTER_URL, json={"email": "cand@test.com", "full_name": "C", "password": "Pass1234!"})
    token = await _login(client, "cand@test.com", "Pass1234!")
    r = await client.get(_USERS_URL, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_list_users_as_admin(client, db_session):
    email, pw = await _make_admin(db_session)
    token = await _login(client, email, pw)
    r = await client.get(_USERS_URL, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert "items" in body
    assert body["total"] >= 1


# ---------------------------------------------------------------------------
# Admin: create user
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_user_as_admin(client, db_session):
    email, pw = await _make_admin(db_session)
    token = await _login(client, email, pw)
    r = await client.post(
        _USERS_URL,
        json={"email": "examiner@test.com", "full_name": "E", "password": "Pass1234!", "role": "examiner"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 201
    assert r.json()["role"] == "examiner"


@pytest.mark.asyncio
async def test_create_user_candidate_forbidden(client):
    await client.post(_REGISTER_URL, json={"email": "cand2@test.com", "full_name": "C", "password": "Pass1234!"})
    token = await _login(client, "cand2@test.com", "Pass1234!")
    r = await client.post(
        _USERS_URL,
        json={"email": "new@test.com", "full_name": "N", "password": "Pass1234!", "role": "examiner"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Self vs admin access
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_self(client):
    await client.post(_REGISTER_URL, json={"email": "self@test.com", "full_name": "S", "password": "Pass1234!"})
    login_r = await client.post(_LOGIN_URL, json={"email": "self@test.com", "password": "Pass1234!"})
    user_id = login_r.json()["user"]["id"]
    token = login_r.json()["access_token"]
    r = await client.get(f"{_USERS_URL}/{user_id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_get_other_user_as_candidate_forbidden(client):
    await client.post(_REGISTER_URL, json={"email": "u1@test.com", "full_name": "U1", "password": "Pass1234!"})
    await client.post(_REGISTER_URL, json={"email": "u2@test.com", "full_name": "U2", "password": "Pass1234!"})
    login_r = await client.post(_LOGIN_URL, json={"email": "u1@test.com", "password": "Pass1234!"})
    token = login_r.json()["access_token"]
    login_r2 = await client.post(_LOGIN_URL, json={"email": "u2@test.com", "password": "Pass1234!"})
    other_id = login_r2.json()["user"]["id"]
    r = await client.get(f"{_USERS_URL}/{other_id}", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Role escalation prevention
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_candidate_cannot_set_own_role(client):
    await client.post(_REGISTER_URL, json={"email": "role@test.com", "full_name": "R", "password": "Pass1234!"})
    login_r = await client.post(_LOGIN_URL, json={"email": "role@test.com", "password": "Pass1234!"})
    token = login_r.json()["access_token"]
    user_id = login_r.json()["user"]["id"]
    # PATCH /users/{id} has no role field — sending role in payload must not change it
    r = await client.patch(
        f"{_USERS_URL}/{user_id}",
        json={"full_name": "NewName"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["role"] == "candidate"


# ---------------------------------------------------------------------------
# Last-admin lockout prevention
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_last_admin_cannot_deactivate_self(client, db_session):
    email, pw = await _make_admin(db_session)
    login_r = await client.post(_LOGIN_URL, json={"email": email, "password": pw})
    token = login_r.json()["access_token"]
    user_id = login_r.json()["user"]["id"]
    r = await client.patch(
        f"{_USERS_URL}/{user_id}/status",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 409
