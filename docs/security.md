# NIGRAN-360 — Security Design

## Authentication
- Passwords hashed with Argon2id (memory-hard, resistant to GPU attacks)
- JWT access tokens (short-lived, 60 min), refresh tokens (7 days)
- Tokens stored in memory on the client; refresh token in httpOnly cookie (Phase 2)

## Authorization
- All permission checks enforced on the backend via dependency injection
- Role checks: administrator > examiner > candidate (non-hierarchical, role-specific)
- Resource-level ownership checks (examiner can only modify their own exams)
- Candidates can only access their own attempts, answers and results

## Data Protection
- Correct answer keys never sent to the frontend during an active attempt
- Results not visible to candidates until examiner publishes
- Verification endpoint returns minimal information (name, exam, score, pass/fail)
- Personal data not embedded in shareable report URLs

## Examination Integrity
- Deadlines computed server-side: `started_at + duration_minutes`
- Submission rejected if `now() > deadline`
- Question order frozen at attempt creation time (JSON snapshot)
- Duplicate active attempt prevention: retake / concurrency policy under review with Person 2 (D3).
  A database-level constraint will be added once the policy is finalised (Phase 4 prerequisite).

## Logging
- Structured JSON logs via Python `logging.config.dictConfig`
- Logs written to stdout (compatible with Docker / systemd log collection)
- HTTP 4xx/5xx requests logged at WARNING / ERROR level with method and path only
- Passwords, tokens, and secrets are never logged
- Validation error field names are logged but not field values

## Dispute Integrity
- Original scores immutable once stored
- Revised scores require explicit examiner action with mandatory reason
- Every state change creates an immutable `DisputeAudit` row

## Input Validation
- Pydantic v2 validates all request bodies on the backend
- Zod validates all form inputs on the frontend
- SQL injection prevented by SQLAlchemy ORM parameterized queries
- File uploads (bulk import) are validated before DB insertion

## Threat Model (Key Risks)
| Threat | Mitigation |
|---|---|
| Candidate sees answer keys | Never returned in attempt API responses |
| Clock manipulation | Server timestamp for all deadlines |
| Replay attack on answer save | Idempotent upsert; no side effects on repeat |
| Unauthorized result access | Published flag + candidate_id check |
| Dispute manipulation | Audit trail; original score preserved |
