# NIGRAN-360 — Security Design

## Authentication (Phase 2 — implemented)
- Passwords hashed with Argon2id (time_cost=2, memory_cost=65536, parallelism=2)
- JWT access tokens (60 min) stored **in Zustand in-memory closure only** — never in localStorage or sessionStorage
- Refresh tokens (7 days) stored in an **HttpOnly SameSite=Lax** cookie; never accessible from JavaScript
- Refresh-token rotation: a successful `/auth/refresh` revokes the old JTI and issues a new refresh token; reuse of a rotated token returns 401
- DB-backed JTI revocation table (`revoked_tokens`) with unique JTI index + expires_at index for cleanup
- CSRF double-submit cookie pattern on `logout` and `refresh`: non-HttpOnly `csrf_token` cookie + `X-CSRF-Token` header
- On page reload, session is restored by calling `/auth/refresh` via the HttpOnly cookie — no credentials in browser storage
- Rate limiting: in-process sliding window, 10 attempts per IP per 15 minutes on `/auth/login`
- Invalid credentials return generic 401 "Invalid credentials" — account existence is not revealed
- Deactivated accounts cannot authenticate (403 returned after password check passes)

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
| XSS token theft | Access token in JS memory, never in DOM storage |
| Refresh token theft | HttpOnly cookie, not reachable from JS |
| CSRF on state-changing auth routes | Double-submit cookie checked on logout + refresh |
| Credential brute-force | Rate limit 10/IP/15 min; constant-time Argon2 verify |
| Account enumeration | Identical 401 for wrong password and unknown email |
| Refresh token reuse (rotation attack) | Rotated token JTI revoked in DB; reuse returns 401 |
| Last-admin lockout | Backend prevents deactivating the last active administrator |
| Role escalation | No role field in self-update; role only set at creation |
| Candidate sees answer keys | Never returned in attempt API responses |
| Clock manipulation | Server timestamp for all deadlines |
| Replay attack on answer save | Idempotent upsert; no side effects on repeat |
| Unauthorized result access | Published flag + candidate_id check |
| Dispute manipulation | Audit trail; original score preserved |
