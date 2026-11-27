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

The test suite uses an **in-memory SQLite database** (`sqlite+aiosqlite:///:memory:`) via `aiosqlite`. No running PostgreSQL is required to run the tests.

The shared `tests/conftest.py` fixture creates and tears down the schema per test function using SQLAlchemy's `Base.metadata.create_all`. Each test gets a fresh, isolated database.

**To run all tests:**
```bash
cd backend
source .venv/bin/activate
pip install -e ".[dev]"   # installs aiosqlite, httpx, pytest-asyncio
pytest
```

**Current test coverage (55 tests passing):**

| Module | Tests |
|---|---|
| `tests/unit/test_password.py` | Argon2id hashing, verify, min-length, salt uniqueness |
| `tests/unit/test_token.py` | JWT roundtrip, type enforcement, tamper rejection, JTI uniqueness, revocation |
| `tests/unit/test_rate_limit.py` | Sliding window, per-IP isolation, reset |
| `tests/integration/test_auth.py` | Register, login, rate limit, /me, logout + revocation, refresh, rotation |
| `tests/integration/test_users.py` | CRUD, admin-only, self vs admin access, role escalation, last-admin lockout |
| `tests/security/test_rbac.py` | Examiner/candidate cross-role, deactivated account, enum-safe error messages |

For integration tests that need PostgreSQL (future phases), use a separate test database and configure `TEST_DATABASE_URL`. Never run destructive tests against the development database.

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
