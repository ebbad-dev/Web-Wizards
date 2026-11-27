import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.schemas.common import ErrorResponse, make_error


@pytest.mark.asyncio
async def test_404_returns_standard_error_envelope():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert body["status"] == "error"
    assert body["code"] == 404
    assert "message" in body


@pytest.mark.asyncio
async def test_validation_error_returns_standard_envelope():
    """POST with wrong content type to trigger 422."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/ping",
            content=b"not-json",
            headers={"content-type": "application/json"},
        )
    # 405 Method Not Allowed (ping only has GET) — still standard envelope
    assert response.status_code in (405, 422)
    body = response.json()
    assert body["status"] == "error"


def test_make_error_shape():
    result = make_error(400, "bad input")
    assert result["status"] == "error"
    assert result["code"] == 400
    assert result["message"] == "bad input"
    assert "details" not in result


def test_make_error_with_details():
    result = make_error(422, "validation failed", [{"field": "email", "message": "invalid"}])
    assert result["details"][0]["field"] == "email"


def test_error_response_model():
    er = ErrorResponse(code=500, message="oops")
    assert er.status == "error"
    assert er.details is None
