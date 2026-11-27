# NIGRAN-360

**Secure Examination Management System** — Web-e-Thon @ Technoverse 5.0, COMSATS University Lahore, 27–28 November 2026.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2 async |
| Database | PostgreSQL 16 |
| Auth | Argon2id + JWT |

## Quick Start (Development)

### Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL 16 running locally (or use Docker Compose)

### Database (Docker)
```bash
docker compose up db -d
```

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp ../.env.example .env     # edit DATABASE_URL if needed
alembic upgrade head         # run migrations
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp ../.env.example .env.local
npm run dev
```

App: http://localhost:5173  
API docs: http://localhost:8000/api/docs

## Test Credentials (Phase 2+)

| Role | Email | Password |
|---|---|---|
| Administrator | admin@nigran.test | Admin360! |
| Examiner | examiner@nigran.test | Exam360! |
| Candidate | candidate@nigran.test | Cand360! |

## Innovation Challenge

**5.4 — Trust & Dispute Resolution**: A transparent, auditable dispute mechanism with immutable audit logs, mandatory resolution notes, and preserved original scores.

## Development Phases

| Phase | Scope | Status |
|---|---|---|
| 1 | Repository init & engineering foundation | ✅ Complete |
| 2 | Authentication & user management | Planned |
| 3 | Examination & question management | Planned |
| 4 | Candidate examination engine | Planned |
| 5 | Monitoring, grading & results | Planned |
| 6 | Trust & dispute resolution | Planned |
| 7 | Reporting & integration | Planned |
| 8 | Testing, security & deployment | Planned |

## Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```
