# Architecture — Nigran 360

## 1. Architecture objective

Extend the existing modular monolith. The current FastAPI service, SQL Server repositories, React/TanStack frontend and proctoring sidecar are sufficient foundations for this scope. Keep deployment and local development simple. Do not split into microservices without concrete evidence that the current architecture cannot meet requirements.

## 2. Current architecture to preserve

- React/TypeScript frontend using existing TanStack routing/query patterns and shared UI components.
- FastAPI API layer with Pydantic request/response models and role dependencies.
- Domain/service layer for exam, identity and attempt rules.
- Repository/data layer backed by SQL Server and `pyodbc`.
- Existing authentication, tenant scoping, audit logging and operational endpoints.
- Proctoring sidecar/browser extension for camera, audio and browser signals.
- ReportLab utilities for PDF report generation.

Phase 0 must produce an accurate component/dependency diagram from the actual repository. This document is a target guide, not permission to relocate modules just for aesthetics.

## 3. Target logical modules

### Identity and access

Re-use existing login, account, role, tenant and session mechanisms. Add only missing permission scopes or dependencies. Avoid duplicating access checks in route handlers; centralize policy in the existing service/dependency pattern.

### Exam management

Own exam metadata, lifecycle transitions, instructions, candidate assignments and exam configuration. Enforce server-side publication/availability validation.

### Question bank

Separate reusable question content from exam/attempt assignment. A question-bank item may be revised, but the attempt uses a frozen assignment snapshot. Support type-specific validation and marking configurations.

### Attempt engine

Own attempt start, immutable snapshot creation, deadline, response persistence, mark-for-review state, save idempotency, submission and expiry. It is the authoritative source of time and accepted response state.

### Monitoring and communication

Re-use existing proctoring events/evidence. Add exam-level announcement records and active attempt summaries. Do not let risk-score code make academic grading or disciplinary decisions.

### Evaluation and results

Separate automatic objective marking, manual written grading, examiner review and result publication. Keep a single, deterministic score calculation service.

### Reporting and analytics

Keep proctoring reports distinct from academic result reports. Reuse existing PDF infrastructure with separate report types/templates and access policies. Analytics must exclude sandbox and unsubmitted attempts.

### Import and sandbox

Use a validation/preview pipeline for imports. Isolate sandbox attempts with a distinct persisted discriminator or separate safe storage boundary and filter every official query accordingly.

## 4. Recommended request/data flows

### Create and publish exam

Frontend → authenticated FastAPI route → exam service → authorization + validation → repository transaction → audit event → typed response. The publication operation must validate question availability/types/marks, schedule, candidate access configuration and candidate preview requirements.

### Start attempt

Candidate frontend → start route → authenticate candidate → validate assignment + exam window + attempt state → transactionally create attempt, freeze question/option/marking snapshot, generate immutable server `deadline_at` and stable attempt metadata → return candidate-safe snapshot with no correctness keys.

### Save response

Candidate frontend → typed response route → authenticate owner → verify active attempt and deadline using server time → validate question belongs to snapshot and answer type/choices → idempotency/version check → persist response transactionally → calculate objective result only according to snapshot marking policy → return acknowledged version and save timestamp.

### Submit and expiry

A single domain operation handles explicit submit and expiry finalization. It must be idempotent. It must finalize only server-accepted responses, calculate or mark pending grading, freeze response mutation and record timestamps. Do not rely on a browser timer to decide authoritative expiry.

### Manual grading and publication

Examiner UI → authorized grading route → verify exam ownership → validate score boundaries and grading state → persist grade and audit event → recompute totals → mark exam result set ready for review → explicit publish action → candidate results endpoint filters to authenticated candidate and published state.

### Network recovery

Browser stores a bounded pending queue in IndexedDB (or existing approved local persistence) using stable idempotency IDs and per-question version/order. On reconnection, retry through the same server validation path. Server responds with accepted/rejected/conflict state. A client wall-clock timestamp is informational only, never authoritative.

## 5. API design principles

- Preserve existing public routes and current payload meanings.
- Use Pydantic schemas and typed frontend API models.
- Extend request/response contracts compatibly where possible; if a breaking schema is necessary, use a versioned route or adapter and keep legacy clients working during transition.
- Do not return correct-answer flags, answer keys, marking schemes or private rubric details to candidates before allowed release.
- Return explicit save status/version, validation errors and deadline state.
- Use stable error codes for expected conditions (for example: `attempt_expired`, `response_conflict`, `result_not_published`, `not_assigned`).
- Keep error bodies safe; do not leak SQL, secrets or stack traces.
- Apply pagination and filters to potentially large lists.

Phase 0 should capture exact existing routes and schemas before designing new endpoints. Prefer extending a route over inventing a parallel route that duplicates the same behavior.

## 6. Data integrity patterns

- SQL Server transactions for attempt start/snapshot creation and submission finalization.
- Unique constraints/indexes for idempotency, one active attempt rules (where applicable), and report token lookup.
- `rowversion` or an explicit integer version for mutable answer records if compatible with the existing schema.
- Stable server-generated IDs and UTC timestamps.
- Immutable per-attempt question, options, ordering and marking scheme.
- Immutable persisted server deadline for new attempts.
- Explicit grading and result publication state transitions.
- Separate sandbox discriminator or data namespace with tests proving it is excluded from production aggregates.

Use existing transaction and repository conventions. Do not issue direct SQL from route handlers.

## 7. UI architecture

Reuse current AppShell/layouts, data hooks, shared components and design tokens. Keep three coherent information architectures:

- Admin: users, roles, tenant/platform administration and audit/ops.
- Examiner: dashboard, exams, question bank, candidates, active monitoring, grading/results, reports/import/sandbox.
- Candidate: available/upcoming/completed exams, instructions, exam runner, announcements and published results.

Do not build multiple disconnected dashboards if current layouts can be extended cleanly. Add loading, empty, permission-denied, stale, offline, pending, saved and retry states. Use semantic buttons/inputs, keyboard navigation and responsive layout.

## 8. Observability

Use existing logs, health and metrics patterns. New operational events should include correlation/attempt/exam IDs where useful but must not contain passwords, tokens, raw answer keys, unnecessary PII or unredacted scratchpad content. Measure failed answer sync, duplicate retries, attempt finalization, import failures and report generation errors through existing mechanisms if available.

## 9. Architecture decisions requiring Phase 0 confirmation

1. Existing exact exam and attempt table schema.
2. Existing transaction/locking strategy for start/save/submit races.
3. Whether `rowversion` is already used or an application version field is safer.
4. Best snapshot representation: normalized tables, JSON snapshot, or a hybrid.
5. How legacy attempts will derive deadlines and read responses.
6. How grading states align with existing `score`, `awarded_marks`, `is_correct` fields.
7. Whether announcement delivery uses TanStack Query polling, server-sent events or an existing realtime channel. Prefer polling if it is adequate and no live channel exists.
8. Whether candidate preferences should be local-only or account-persisted; choose the smallest approach that meets retention expectations.
9. Whether a new PDF report generator can reuse current layout helpers without mixing proctoring and academic data.
