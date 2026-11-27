from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_readiness_db_unavailable():
    """Readiness returns 503 when the database is unreachable."""

    # Patch the engine used inside main.py's readiness endpoint.
    # We replace the entire engine with a mock whose .connect() context manager raises.
    mock_engine = MagicMock()
    mock_ctx = AsyncMock()
    mock_ctx.__aenter__.side_effect = Exception("connection refused")
    mock_ctx.__aexit__ = AsyncMock(return_value=False)
    mock_engine.connect.return_value = mock_ctx

    with patch("app.main.engine", mock_engine):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["database"] == "unreachable"
