"""Security tests: RBAC enforcement and cross-role boundary checks."""
from __future__ import annotations

import uuid

import pytest

from app.models.user import User
from app.services.password import hash_password

_REGISTER_URL = "/api/v1/auth/register"
_LOGIN_URL = "/api/v1/auth/login"
_USERS_URL = "/api/v1/users"


async def _make_user(db_session, role: str) -> tuple[str, str]:
    email = f"{role}-{uuid.uuid4().hex[:6]}@test.com"
    password = "RbacPass1!"
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        full_name=f"Test {role.capitalize()}",
        hashed_password=hash_password(password),
        role=role,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return email, password


async def _login(client, email: str, password: str) -> str:
    r = await client.post(_LOGIN_URL, json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.mark.asyncio
async def test_examiner_cannot_list_all_users(client, db_session):
    email, pw = await _make_user(db_session, "examiner")
    token = await _login(client, email, pw)
    r = await client.get(_USERS_URL, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_examiner_cannot_create_administrator(client, db_session):
    email, pw = await _make_user(db_session, "examiner")
    token = await _login(client, email, pw)
    r = await client.post(
        _USERS_URL,
        json={"email": "badadmin@test.com", "full_name": "Bad", "password": "Pass1234!", "role": "administrator"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_candidate_cannot_create_any_user(client, db_session):
    email, pw = await _make_user(db_session, "candidate")
    token = await _login(client, email, pw)
    r = await client.post(
        _USERS_URL,
        json={"email": "newuser@test.com", "full_name": "N", "password": "Pass1234!", "role": "candidate"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_no_access_without_token(client):
    r = await client.get(_USERS_URL)
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_deactivated_account_cannot_login(client, db_session):
    email = f"inactive-{uuid.uuid4().hex[:6]}@test.com"
    password = "Pass1234!"
    user = User(
        id=str(uuid.uuid4()),
        email=email,
        full_name="Inactive",
        hashed_password=hash_password(password),
        role="candidate",
        is_active=False,
    )
    db_session.add(user)
    await db_session.commit()

    r = await client.post(_LOGIN_URL, json={"email": email, "password": password})
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_credentials_error_does_not_reveal_account_existence(client):
    # Non-existent email and existing email with wrong password must both return 401
    r1 = await client.post(_LOGIN_URL, json={"email": "ghost@test.com", "password": "Any1Pass!"})
    await client.post(_REGISTER_URL, json={"email": "real@test.com", "full_name": "R", "password": "Pass1234!"})
    r2 = await client.post(_LOGIN_URL, json={"email": "real@test.com", "password": "WrongPass1!"})
    assert r1.status_code == 401
    assert r2.status_code == 401
    assert r1.json()["message"] == r2.json()["message"]
