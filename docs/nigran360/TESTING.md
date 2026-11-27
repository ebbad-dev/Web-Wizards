# Testing and Verification Strategy — Nigran 360

## 1. Testing philosophy

A feature is not complete because the UI renders. Each requirement must be verified across frontend, API, service, database and authorization boundaries. Every phase must run targeted tests and the existing regression suite. Do not remove/skip existing tests to make a change pass.

## 2. Establish the baseline first

In Phase 0, inspect the current scripts and run the repository's documented commands. The README currently documents a PowerShell quality command:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_quality_checks.ps1
```

It also lists operational commands such as `npm run quality`, `npm run preflight`, `npm run health` and SQL Server smoke helpers. Verify current package scripts and CI before relying on a command; do not invent a command and report it as run.

Where available, run:

- Python unit/regression suite.
- Python compile/lint/type checks actually configured in the repo.
- Frontend TypeScript typecheck.
- Frontend production build.
- Migration tests.
- SQL Server live smoke tests using the intended test database.
- Existing security regression tests.

Record exact commands, environment, counts and failures.

## 3. Required test layers

### Unit tests

Test validation, state transitions, marking rules, score calculation, deadline checks, idempotency, import validators, report token verification and analytics calculations.

### Service/repository integration tests

Test exam/attempt/question/grade/publication operations against repositories and transactions. Use SQL Server integration tests for SQL-specific locking, constraints, `rowversion`, migrations and query behavior. Mocking alone is insufficient for database-specific invariants.

### API tests

Test successful and forbidden requests for all roles, wrong owners/tenants, malformed payloads, not-assigned candidates, unpublished results, expired attempts and duplicate requests. Assert response schemas and no sensitive fields.

### Frontend tests

Test question type rendering, navigation, mark-for-review states, autosave indicators, retry/conflict states, timer display, candidate result visibility, scratchpad scope and responsive/keyboard behavior.

### End-to-end tests

Exercise full journeys for admin, examiner and candidate. Include one real attempt and one sandbox attempt. Demonstrate failure recovery with a controlled network interruption.

### Regression tests

Protect existing auth, password reset, exam CRUD/publish, assignments/join, attempt save/submit, expiry/idempotency, proctoring startup, event ingestion, evidence, reports, tenant isolation and ops/health behavior.

## 4. Phase acceptance tests

### Phase 0

- Baseline branch/commit/status recorded.
- Baseline tests run and result documented.
- Existing routes/schemas/tables/migrations identified.
- Risks and compatibility design approved.
- No product feature code changed.

### Phase 1 — question bank and types

- Existing single-answer MCQ creation/edit/publish/attempt flow still works.
- Multiple-select supports selecting zero/one/many values as allowed and rejects invalid IDs.
- Written question persists response text safely.
- Marking scheme is versioned and validated.
- Randomized order is stable for the life of an attempt.
- Editing source question after start does not mutate attempt snapshot.
- Candidate response never contains correctness keys.

### Phase 2 — exam and candidate management

- Existing lifecycle/status values remain compatible.
- Draft cannot be accessed by candidates.
- Candidate sees only assigned authorized exams and correct access state.
- Schedule/time window enforced by server.
- Examiner preview matches candidate-safe view.
- Revoked/unassigned candidate cannot start or read an attempt.

### Phase 3 — workspace

- All four question status states render correctly.
- Mark-for-review persists through refresh.
- Navigation/final review accurately reflects saved answers.
- Preferences persist and never hide mandatory exam controls.
- Scratchpad is isolated to candidate/attempt, excluded from grade and not exposed to examiner by default.
- Existing proctoring startup and timer remain functional.

### Phase 4 — network resilience

- Online save shows pending/saving then saved only after API acknowledgement.
- Offline change shows pending and is queued within a defined bound.
- Reconnect retries safely without duplicate writes or overwriting newer responses.
- Duplicate idempotency key returns consistent state.
- Invalid/expired writes are rejected by server.
- Client clock changes do not extend the exam.
- Refresh during valid attempt restores server-acknowledged state and attempts pending reconciliation.
- User sees explicit unresolved sync failures; no silent data loss claim.

### Phase 5 — monitoring/announcements

- Examiner sees only authorized exams/attempts.
- Progress is based on persisted response/attempt state.
- Announcement is visible only to intended candidates and correct exam.
- Announcement creation/editing is audited.
- Monitoring incidents remain review indicators, not automatic grading decisions.

### Phase 6 — grading/results/analytics

- Single MCQ auto-grading preserves legacy semantics.
- Multiple-select grading follows exact configured scheme.
- Written response remains pending until authorized examiner grades it.
- Marks below zero or above max are rejected unless an explicitly approved scoring rule says otherwise.
- Total is reproducible and bounded by configured exam marks.
- Result is invisible before publication and visible only to the correct candidate after publication.
- Analytics use submitted real attempts and exclude sandbox/in-progress records.
- Small sample size is communicated.

### Phase 7 — secondary features

- Academic PDF is distinct from proctoring PDF and contains real performance values.
- Unauthorized users cannot create/download it.
- Sandbox attempt cannot affect real attendance, score, analytics, export or candidate results.
- CSV and JSON imports validate and show errors before commit.
- Invalid file does not partially contaminate the database under default all-or-nothing mode.
- Report QR/token verifies authenticity with minimal public fields and cannot be trivially enumerated.
- Feature 4.1, 4.5, 4.7 and 4.8 are explicitly re-verified.

### Phase 8 — integrated readiness

- Full role journey E2E passes.
- Full regression, typecheck, production build, migration and SQL smoke pass where environment permits.
- Backup/restore rehearsal is documented.
- Security/tenant/access checks pass.
- Responsive/accessibility review completed.
- Demo accounts/data are fictional and safe.
- README contains fresh setup/test/demo instructions.
- Competition cutoff has been checked; prohibited post-cutoff actions are not performed.

## 5. Important edge cases

- Two rapid response saves to one question arrive out of order.
- Same save request is retried after a timeout but actually committed the first time.
- Candidate submits while a response save is still in flight.
- Server deadline passes while the browser is offline.
- Exam duration or question bank record is edited after an attempt starts.
- Candidate assignment is revoked during an attempt.
- Examiner grades a response twice or two graders act concurrently.
- Result publication is repeated.
- Candidate tries to request another candidate's attempt/result/report.
- Sandbox request attempts to set a real exam or real user ID.
- Import contains duplicate emails, malformed JSON, invalid option references, oversized rows and formula-like strings.
- Public report verification token is revoked or malformed.
- Tenant contains same local-looking IDs where globally unique assumptions may fail.

## 6. Evidence and honest reporting

For each phase, preserve useful command output, test names/counts and screenshots only where permitted. Do not store production PII or secrets in test artifacts. Distinguish `PASS`, `FAIL`, `NOT RUN` and `BLOCKED`. An inaccessible SQL Server integration environment is not a pass; it is a documented blocker plus any available unit/mock coverage.
