# NIGRAN-360 — Architecture

## Pattern

Modular monolith with a decoupled React SPA frontend and FastAPI REST backend.

## Components

### Frontend (React SPA)
- React 19 + TypeScript + Vite
- TailwindCSS + shadcn/ui for design system
- React Router for client-side routing
- TanStack Query for server state
- Zustand for local UI state
- React Hook Form + Zod for forms and validation
- Axios with JWT Bearer token interceptors

### Backend (FastAPI REST)
- FastAPI + Pydantic v2 for API layer
- SQLAlchemy 2 async + asyncpg for ORM and DB driver
- Alembic for database migrations
- Argon2id for password hashing
- python-jose for JWT tokens
- ReportLab + qrcode for PDF and QR generation

### Database
- PostgreSQL 16

## Business Modules (Backend)

| Module | Responsibility |
|---|---|
| auth | Login, token issuance, refresh |
| users | User CRUD, role management |
| examinations | Exam lifecycle (draft→published→ongoing→completed) |
| questions | Question bank, choices, categories, difficulty |
| enrollment | Candidate enrollment per exam |
| attempts | Attempt creation, answer autosave, deadline enforcement |
| monitoring | Active attempt tracking, events, announcements |
| grading | Auto-grade MCQ, manual grade written |
| results | Score calculation, publication control |
| disputes | 5.4 Trust & Dispute Resolution workflow |
| analytics | Question-level and exam-level performance insights |
| reports | PDF report generation with verification codes |
| verification | QR-based report authenticity check |

## Key Design Decisions

### Server-Authoritative Timing
Attempt deadlines are computed from `started_at + duration_minutes` on the server and stored in the DB. The frontend uses the server-returned deadline, never the device clock.

### Question Snapshot
`ExamQuestion` links questions to exams with optional mark overrides. Attempts store a frozen `question_order` JSON snapshot so later edits to the question bank cannot alter active attempts.

### Answer Persistence
`AttemptAnswer` rows are upserted on every save. The frontend shows "saved" only after HTTP 200. Offline drafts are queued in memory and retried; the network status indicator shows pending state.

### Dispute Audit Trail
Every state transition of a `Dispute` creates a `DisputeAudit` row with actor, timestamp and note. Original scores are preserved; revised scores require explicit examiner input.

## ERD Summary

```
users 1──* examinations (created_by)
users 1──* enrollments (candidate_id)
examinations 1──* enrollments
examinations 1──* exam_questions
questions 1──* exam_questions
questions 1──* choices
examinations 1──* attempts
users 1──* attempts (candidate_id)
attempts 1──* attempt_answers
questions 1──* attempt_answers
attempts 1──1 results
results 1──* disputes
disputes 1──* dispute_audits
examinations 1──* exam_events
examinations 1──* announcements
```

## Deployment Topology

```
Browser → Vite SPA (port 5173 dev / nginx prod)
              ↓ /api/v1/* proxy
         FastAPI (port 8000)
              ↓
         PostgreSQL (port 5432)
```
