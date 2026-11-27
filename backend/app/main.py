import logging
import logging.config
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.database.session import engine
from app.schemas.common import make_error

# ---------------------------------------------------------------------------
# Logging setup (D5)
# ---------------------------------------------------------------------------

LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "format": '{"time": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "uvicorn.access": {"level": "WARNING"},
        "sqlalchemy.engine": {"level": "WARNING"},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("nigran360")


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("NIGRAN-360 starting up")
    yield
    logger.info("NIGRAN-360 shutting down")


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="NIGRAN-360",
    description="Secure Examination Management System API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


# ---------------------------------------------------------------------------
# Global exception handlers (D4)
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning("HTTP %s %s → %d", request.method, request.url.path, exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content=make_error(exc.status_code, str(exc.detail)),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for err in exc.errors():
        field = ".".join(str(loc) for loc in err.get("loc", []) if loc != "body")
        details.append({"field": field or None, "message": err["msg"]})
    logger.info("Validation error %s %s: %d field(s)", request.method, request.url.path, len(details))
    return JSONResponse(
        status_code=422,
        content=make_error(422, "Request validation failed", details),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content=make_error(500, "An unexpected error occurred"),
    )


# ---------------------------------------------------------------------------
# Health / Readiness endpoints
# ---------------------------------------------------------------------------

@app.get("/api/health", tags=["ops"])
async def health() -> dict[str, str]:
    """Liveness probe — returns ok when the process is running."""
    return {"status": "ok", "app": "NIGRAN-360"}


@app.get("/api/ready", tags=["ops"])
async def readiness() -> JSONResponse:
    """Readiness probe — returns ok only when PostgreSQL is reachable."""
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=200,
            content={"status": "ok", "database": "connected"},
        )
    except Exception as db_exc:
        logger.error("Readiness check failed: %s", db_exc)
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "unreachable",
                     "detail": "Database connection failed"},
        )
