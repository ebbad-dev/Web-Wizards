from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorResponse(BaseModel):
    """Standard error envelope returned by all NIGRAN-360 error responses."""
    status: str = "error"
    code: int
    message: str
    details: list[ErrorDetail] | None = None


class HealthResponse(BaseModel):
    status: str
    app: str


class ReadinessResponse(BaseModel):
    status: str
    database: str
    detail: str | None = None


def make_error(code: int, message: str, details: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"status": "error", "code": code, "message": message}
    if details:
        payload["details"] = details
    return payload
