"""Shared pytest fixtures for all test modules."""
from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401 — registers all ORM models
from app.core.rate_limit import reset_rate_limit
from app.database.session import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# HTTPX test client always uses "testclient" as the host/IP.
_TEST_IP = "testclient"


@pytest.fixture(autouse=True)
def reset_rate_limiter_between_tests():
    # ASGITransport may expose client.host as "testclient", "127.0.0.1", or None → "unknown".
    for ip in (_TEST_IP, None, "127.0.0.1"):
        reset_rate_limit(ip)
    yield
    for ip in (_TEST_IP, None, "127.0.0.1"):
        reset_rate_limit(ip)


@pytest_asyncio.fixture(scope="function")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(engine):
    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
