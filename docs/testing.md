# NIGRAN-360 — Testing Guide

## Backend Testing

### Prerequisites

- Python 3.11+ installed
- PostgreSQL 16 running locally (or via Docker Compose — see below)
- Backend virtual environment created

### Environment Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"          # Installs app + all dev dependencies (greenlet, ruff, mypy, pytest, etc.)
cp ../.env.example .env          # Edit DATABASE_URL and SECRET_KEY as needed
```

The editable install (`-e ".[dev]"`) ensures `sqlalchemy[asyncio]` and `greenlet` are installed correctly.

### Running All Backend Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

### Running Specific Tests

```bash
# Health and ping only
pytest tests/test_health.py -v

# With coverage report
pytest --cov=app --cov-report=term-missing

# Stop on first failure
pytest -x
```

### Database Configuration for Tests

The existing test suite (health, ping, error handling) uses an ASGI transport and does **not** require a live database.

Future tests that touch the database (Phase 2+) must use a separate test database. Set `TEST_DATABASE_URL` in `.env` and configure a pytest fixture that creates and tears down the schema using Alembic or SQLAlchemy directly. Never run destructive tests against the development database.

### Alembic Migration Testing

**Always test migrations against a clean, disposable database — never the development database with real data.**

```bash
# Start a disposable test DB via Docker
docker run -d --rm \
  --name nigran-migrate-test \
  -e POSTGRES_USER=nigran \
  -e POSTGRES_PASSWORD=nigran360 \
  -e POSTGRES_DB=nigran360_test \
  -p 5433:5432 \
  postgres:16

# Wait for readiness
docker exec nigran-migrate-test pg_isready -U nigran

# Point Alembic at the test database
DATABASE_URL=postgresql+asyncpg://nigran:nigran360@localhost:5433/nigran360_test \
  alembic upgrade head

# Check revision
DATABASE_URL=postgresql+asyncpg://nigran:nigran360@localhost:5433/nigran360_test \
  alembic current

# Stop and discard when done
docker stop nigran-migrate-test
```

## Frontend Testing

### Prerequisites

- Node.js 20+ installed
- Dependencies installed: `npm install` from `frontend/`

### Running Frontend Tests (Vitest)

```bash
cd frontend
npm test          # run once (CI mode)
npm run test      # alias
```

### Frontend Type Checking

```bash
cd frontend
npx tsc -b --noEmit
```

### Frontend Production Build

```bash
cd frontend
npm run build
```

A clean exit (exit code 0) with output in `frontend/dist/` confirms the build is correct.

### Frontend Linting

```bash
cd frontend
npx oxlint src/
```

## Backend Code Quality

### Ruff (lint)

```bash
cd backend
source .venv/bin/activate
ruff check app/ tests/
```

### Ruff (format check only)

```bash
ruff format --check app/ tests/
```

### Mypy (type checking)

```bash
cd backend
source .venv/bin/activate
mypy app/
```

## API Manual Verification

Start the backend:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Then:

```bash
# Liveness
curl http://localhost:8000/api/health

# Readiness (requires DB running)
curl http://localhost:8000/api/ready

# Ping
curl http://localhost:8000/api/v1/ping

# OpenAPI JSON
curl http://localhost:8000/api/openapi.json | python3 -m json.tool | head -20
```

## Safe Test Database Practices

- Never run `alembic downgrade` or `DROP TABLE` on the development database unless it was created solely for testing.
- Use Docker containers with `--rm` for disposable migration tests.
- Never store test credentials in committed files. Use environment variables.
- The `DATABASE_URL` in `.env` is gitignored and must not be committed.
