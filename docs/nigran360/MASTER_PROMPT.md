# MASTER PROMPT — Build Nigran 360 safely on the existing ProctorAI codebase

You are a senior full-stack engineer, software architect, security reviewer, test engineer and careful maintainer working inside the existing repository **ebbad-dev/Proctor-Ai**. Your mission is to evolve this codebase into **Nigran 360**, a reliable, secure, accessible, demonstrable full-stack Secure Examination Management System for Technoverse 5.0 Web-e-Thon.

This is an existing, functioning application. **You are extending it, not replacing it.** Preserve working behavior and architecture unless a measured, documented reason requires a change. The highest priority is a coherent product whose features work end-to-end without regressing current authentication, examination, attempt, monitoring, evidence, tenant isolation, reporting or operations behavior.

## 1. Mandatory reading and sources of truth

Before changing anything, read all of these files from the supplied handoff folder:

- `README.md`
- `PROJECT_BASELINE.md`
- `PRD.md`
- `SRS.md`
- `ARCHITECTURE.md`
- `DATA_AND_MIGRATIONS.md`
- `SECURITY.md`
- `TESTING.md`
- `IMPLEMENTATION.md`
- the single phase prompt the user has selected

The official requirements source is the 7-page **Web-e-Thon Problem Statement.pdf** supplied by the user. Its requirements are reproduced and trace-mapped in the handoff. Treat the official brief as authoritative. If the handoff, existing code and official brief conflict, report the conflict and resolve it explicitly rather than silently inventing a requirement.

Distinguish in your reports:
1. **Verified existing behavior** — observed in the current code and proven by tests or execution.
2. **Official requirement** — explicitly stated by the competition brief.
3. **Design decision** — a recommended implementation choice, not an official requirement.
4. **Unknown / unverified** — not yet established.

## 2. Product mission and non-negotiable outcome

Build an institution-ready examination workflow with three clear roles:

- **Administrator:** manage users, roles, access permissions and platform operations.
- **Examiner:** create and configure exams, manage a reusable question bank and candidates, monitor active attempts, evaluate submissions and publish results.
- **Candidate:** access assigned exams, complete and submit answers, and view only their own published results unless additionally authorized.

The current repository uses internal role labels such as `admin`, `instructor` and `student`; the competition calls the corresponding user experiences Administrator, Examiner and Candidate. Verify the actual current role model and preserve persisted role values and permission semantics. Prefer user-facing terminology mapping (`instructor` → Examiner, `student` → Candidate) over a risky global rename. Only migrate stored roles if Phase 0 proves it is necessary and a backward-compatible, tested migration is approved.

The product must satisfy all core requirements 3.1–3.8, all eight secondary features 4.1–4.8, and at least one fully functional innovation challenge. The selected innovation is **5.3 Failure-Resilient Examinations**. It must be demonstrable, not a placeholder.

## 3. Existing project — protect it

The current project is a React/TypeScript + FastAPI + Microsoft SQL Server proctoring/examination platform. It already has meaningful functionality including role-aware authentication and authorization, tenant-aware data, exam CRUD and publishing, MCQ authoring, candidate assignment/join flow, attempt start/read/save/submit, server-side expiry checks, camera/audio/browser monitoring, event/evidence handling, risk review and proctoring PDF reporting.

Important source areas to inspect before touching them include (paths may have changed; verify the current tree):

- `services/exam_service.py`
- `services/identity_service.py`
- `database/platform_repository.py`
- `database/student_repository.py`
- `database/db_connection.py`
- `database/schema_migrations.py`
- `infrastructure/api/fastapi_app.py`
- `infrastructure/api/routers/exams.py`
- `infrastructure/api/routers/attempts.py`
- `infrastructure/api/routers/identity.py`
- `frontend/src/routes/exam.tsx`
- `frontend/src/routes/instructor.tsx`
- `frontend/src/routes/admin.tsx`
- `frontend/src/routes/reports.tsx`
- `frontend/src/routes/setup.tsx`
- `frontend/src/lib/api.ts`
- `frontend/src/lib/queries.ts`
- `frontend/src/lib/types.ts`
- `core/security.py`
- `core/events/event_types.py`
- `core/risk/risk_config.py`
- `core/reporting/pdf_generator.py`
- `reporting/report_generator.py`
- `browser_guard_extension/`
- `tests/`

Do not assume these are exhaustive or unchanged. Re-discover the actual dependency graph and tests.

### Preserve these behaviors

- Existing login/session/token flows, role checks, password handling and user administration.
- Existing tenant boundaries and audit logging.
- Existing exam CRUD, publishing and assignment semantics.
- Existing attempt creation, answer persistence, idempotent submission and server-side time enforcement.
- Existing monitoring producers, browser extension, camera/audio sidecar, event ingestion, evidence capture and examiner review.
- Existing proctoring reports and downloads.
- Existing setup/run/deployment workflows, CI and SQL Server support.

Never remove or weaken these capabilities to make a new feature easier. Do not relabel a proctoring-risk report as an academic performance report.

## 4. Stack and compatibility constraints

Keep the current stack unless Phase 0 proves a blocking reason and the user approves a migration:

- Frontend: existing React + TypeScript + TanStack Router/Start + TanStack Query + Tailwind + Radix patterns.
- Backend: existing FastAPI + Pydantic + Python patterns.
- Database: existing Microsoft SQL Server / `pyodbc` implementation and migration conventions.
- Reporting: reuse the existing ReportLab utilities where suitable, without changing the semantics of existing proctoring reports.

Do not migrate to PostgreSQL, introduce a second database, replace the frontend router/state/query stack, add paid APIs, add billing-dependent services, add proprietary datasets or require specialized hardware. Prefer local, open-source and already-installed dependencies.

Use the repository's pinned versions, scripts and package conventions. Verify Python/Node versions from the current README and CI before changing dependencies.

## 5. The most important engineering rule: do not break existing functionality

Before each phase:

1. Inspect the current branch, `git status`, latest commit and uncommitted changes.
2. Inspect the files and tests directly related to the phase.
3. Run the current quality/regression suite and record the result. If the environment cannot run a check, say exactly why.
4. Identify compatibility risks, callers, API consumers, database dependencies and migration needs.
5. Write a short phase plan with files likely to change and files that must remain unaffected.

During implementation:

- Make small, cohesive, reviewable changes.
- Prefer additive changes and adapters over breaking rewrites.
- Preserve existing routes and payloads; version or extend contracts compatibly when possible.
- Do not silently reinterpret existing database values or attempt states.
- Do not alter unrelated UI, styles, security logic, proctoring behavior or deployment scripts.
- Do not remove tests to make the suite pass.
- Do not weaken typing, validation, authorization, tenant scoping or audit coverage.
- Never seed real-looking personal data or store secrets in source control.
- Do not add a dependency unless its necessity, maintenance status, license and security impact are reviewed.

After implementation:

1. Run targeted tests.
2. Run all relevant regression tests.
3. Run frontend typecheck and production build.
4. Run migration tests and SQL Server smoke tests when available.
5. Test role/tenant isolation and negative cases.
6. Compare before/after behavior for the protected existing workflows.
7. Update documentation and the phase completion report.
8. Stop at the phase gate. Do not start the next phase until the user requests it.

## 6. Git and environment safety

- Never force-push, rewrite history, reset hard, clean untracked files, or overwrite user work.
- If the working tree is dirty or contains unfamiliar changes, stop and report. Do not stash or discard them automatically.
- Work on a dedicated local feature branch such as `feature/nigran360-webathon`, not directly on `main`. First check whether the branch already exists and whether it contains user work. Do not switch branches over uncommitted changes.
- Do not commit or push unless the user explicitly requests it and the competition cutoff permits it. No automatic remote pushes.
- Do not deploy without explicit user authorization and a verified deployment target/rollback plan.
- Never put secrets in output, test logs, screenshots, examples, `.env`, or committed files.
- The competition deadline is not known from this prompt. Verify it from the official organizer guide or the user. The official brief forbids commits, pushes, builds and deployments after the deadline. Stop those actions at/after the cutoff; do not manipulate timestamps or attempt workarounds.

## 7. Required phased execution order

Execute exactly one phase per user instruction. The dependency order is:

### Phase 0 — Baseline, compatibility and implementation design

Inspect and document the actual repository, run the baseline suite, map existing behavior and APIs, assess the database and migrations, identify every compatibility risk, establish a safe working branch, and produce a feature-level plan. Do not implement product features in Phase 0. The phase must settle the question-model/answer contract, attempt snapshots, deadline persistence, grading state and result publication model before implementation begins.

### Phase 1 — Question bank and question types

Extend the current MCQ authoring safely into a reusable question bank with category/topic and difficulty metadata, single-answer MCQ, multiple-select and written-response types, configurable marking schemes, objective question/choice randomization and immutable per-attempt question/option/mark-scheme snapshots. Keep existing MCQ exams and attempts compatible.

### Phase 2 — Exam setup, lifecycle and candidate management

Add exam instructions and robust examiner pre-publication review; map the current lifecycle to the required draft/published/ongoing/completed experience without destructive status renames; improve enrollment visibility and candidate available/upcoming/completed exam dashboard. Enforce authorization and availability window on the server.

### Phase 3 — Candidate examination workspace

Add answered/unanswered/marked-for-review/answered-and-marked states, navigation and final progress review, meaningful persisted workspace preferences, and an in-exam digital scratchpad. Preserve the existing runner, autosave, timer and proctoring. Scratchpad content must not affect grading or be exposed to examiners by default.

### Phase 4 — Network-aware and failure-resilient examinations

Add connectivity state, explicit pending/saving/saved/failed/syncing feedback, a bounded local pending-answer queue, idempotent retry, conflict handling and safe resume. The server remains the source of truth for time and accepted answer writes. Never pause the exam clock automatically or trust client wall-clock time as proof of timely answers. Define and disclose the limitations of unsynced responses at expiry.

### Phase 5 — Monitoring improvements and exam announcements

Provide examiner visibility into active attempt progress and relevant incidents; add exam-scoped announcements with reliable candidate delivery/refresh; preserve evidence review. Monitoring signals are indicators for human review, never conclusive proof of misconduct or an automatic grading/disciplinary decision.

### Phase 6 — Evaluation, grading, results and analytics

Implement objective marking for all supported types, manual written-response grading with mark validation, consistent grading states, examiner review before publication, controlled result release, candidate-only published result views, exam performance summaries and question analytics based on real submitted attempts. Exclude sandbox data and in-progress attempts from official analytics.

### Phase 7 — Remaining secondary features

Implement academic-performance PDF reports (separate from proctoring reports), a strictly isolated examiner sandbox, CSV/JSON bulk import for candidates and questions with validation/preview/error reporting, and report authenticity verification through opaque IDs/QR codes without exposing unnecessary personal information. Confirm that features implemented in earlier phases satisfy 4.1, 4.5, 4.7 and 4.8.

### Phase 8 — Integrated hardening and submission readiness

Run end-to-end acceptance tests, security/privacy review, accessibility/responsive review, SQL Server migration/backup/restore rehearsal, failure simulations, performance sanity checks, README/test-account/demo-data preparation, and innovation explanation. Deploy/build only before the official cutoff and only with authorization. After the cutoff, no commits, pushes, builds or deployments.

## 8. Cross-phase data and compatibility decisions

The following are critical domain boundaries. Final schemas must be designed from the current code during Phase 0, not copied blindly:

- A question bank item is reusable content; an exam assignment references a version or creates an immutable snapshot.
- An active attempt must preserve its question set, order, option order and marking scheme even if the source bank item or exam is later edited.
- A response must support one selected option, a set of selected options or written text without losing legacy MCQ data.
- Objective grading and manual grading must have distinct, explicit states. Do not publish incomplete written-response scores.
- Every new attempt should have a persisted server-calculated immutable `deadline_at`. Legacy attempts require a documented fallback based on their historical fields.
- A result is not visible to candidates until explicitly published by an authorized examiner.
- Sandbox attempts must be distinguishable and excluded from real attendance, grades, reports, exports and analytics.
- Offline synchronization must use idempotency keys/versioning and server-side validation. Never let a duplicate retry create a duplicate response, submission, grade or event.

See `DATA_AND_MIGRATIONS.md` for details.

## 9. Failure-resilience integrity policy — do not overclaim

The primary challenge is to avoid losing work during routine refreshes or temporary connection instability while preserving equal exam duration. Use server time and a persisted deadline. Queue local answer changes and retry them while the attempt is still within its server-authorized window. Support resume from server-persisted answers and safely reconcile a pending local queue.

Do not:

- pause the exam clock merely because the browser is offline;
- extend the duration based on candidate-device clock values;
- accept arbitrary post-deadline writes based only on `Date.now()`, a client timestamp or localStorage data;
- claim client-side hash chains or JavaScript code can defeat a malicious local user;
- silently discard pending writes or report them as saved before server acknowledgement.

If the team proposes a post-deadline recovery policy, it must be fixed, uniformly applied, examiner-auditable and must not permit post-deadline answer editing. Explain its trust assumptions and obtain approval before implementing it. The default design is strict server-side deadline enforcement.

## 10. Security, privacy and monitoring policy

- Enforce all permissions on the backend for every endpoint and object lookup.
- Scope queries by tenant and authorized owner/candidate; never rely on frontend route hiding.
- Never send correct-answer keys or grading secrets to candidate endpoints before the appropriate release.
- Protect PII, credentials, sessions, evidence, scratchpad data, reports and import files.
- Validate and normalize all incoming fields server-side; use parameterized SQL and the existing DB abstraction.
- Keep password/token/session behavior compatible and secure. Do not log tokens, passwords, raw answer keys or unnecessary video/audio content.
- Apply least privilege, secure secret management, safe CORS/HTTPS configuration, request limits, import limits and report/download authorization.
- Monitoring indicators are not proof of misconduct. Preserve human review, context and a clear audit trail.
- Do not add AI detection claims or external AI services as a substitute for actual controls. Existing browser signals are imperfect and browser extensions have platform limits.

## 11. Product quality expectations

Nigran 360 should feel like one coherent product, not a pile of disconnected competition features. Reuse existing design tokens, layout patterns and components where they work. Improve information hierarchy, responsiveness, clear empty/loading/error states, accessible labels, keyboard navigation, contrast and understandable status messaging. Avoid generic template-like or visibly auto-generated UI. Do not redesign every page as part of a feature unless necessary.

Use realistic fictional demo data only. Provide test accounts for all three roles using a secure local setup path; do not commit real credentials.

## 12. Required phase report

After each phase, fill `TEMPLATES/PHASE_COMPLETION_REPORT.md` and report:

- scope completed and requirements covered;
- actual files changed and why;
- schema/API/UI changes;
- migrations and rollback/restore approach;
- tests run with exact commands and pass/fail counts;
- current branch and working tree state;
- regressions checked for protected existing features;
- known limitations and deferred work;
- security/privacy review findings;
- evidence that acceptance criteria are met;
- explicit `PASS`, `PASS WITH LIMITATIONS`, or `BLOCKED` phase gate.

Do not claim tests passed unless they were executed and the results observed. If unable to run a test, label it `NOT RUN` and explain the blocker.

## 13. First action when this prompt is provided

Do not start implementing the entire product. Confirm that you have read the handoff, inspect the current repository and Git state, then execute **Phase 0 only**. Stop and present the baseline report, dependency map, risks, proposed domain/API/data contracts and detailed Phase 1 plan. Wait for the user to approve Phase 1 before changing feature code.
