# Project Baseline — Nigran 360 starting point

## Baseline snapshot

This handoff was prepared against the public repository `https://github.com/ebbad-dev/Proctor-Ai`.

- Default branch: `main`
- Verified head at handoff preparation: `8eb5c9fe4229faf8e5d11facba934dc9d8058a1d`
- Commit subject: `Extract exam and attempt domain for Phase 2`
- Commit date: 2026-11-27T05:41:25Z
- The latest CI run previously observed for this revision completed successfully. That is a historical baseline only; the coding agent must rerun current checks in its own environment.

**Do not assume this remains the current head when implementation starts.** Recheck the branch and commit, inspect `git status`, and record the actual working copy state.

## Verified technology baseline

- Frontend: React 19 + TypeScript, TanStack Router/Start, TanStack Query, Tailwind CSS, Radix UI, Recharts.
- Backend: Python + FastAPI + Pydantic + Uvicorn.
- Database: Microsoft SQL Server through `pyodbc`.
- Proctoring sidecar: camera/audio/browser signals; README mentions OpenCV, Flask MJPEG and sounddevice.
- Reporting: ReportLab PDF generation.
- CI: GitHub Actions on Windows runner (verify latest workflow before relying on this detail).
- Local runtime documented in README: frontend port 8080, FastAPI port 5051, video sidecar port 5050.
- README setup mentions Python 3.12.13 and Node.js 24. Confirm exact toolchain in pinned files and CI.

## Existing role terminology

The inspected application uses internal role names including `admin`, `instructor` and `student`; the competition brief uses Administrator, Examiner and Candidate. Treat these as product-facing role names mapped to the existing internal roles unless Phase 0 discovers a different live implementation. Preserve stored role values and existing admin/instructor privilege behavior. Do not globally rename role strings or tokens as a UI-labeling task.

## Existing areas and functionality to protect

| Area | Existing capability observed in the baseline | Protection rule |
|---|---|---|
| Identity | Admin/instructor/student roles, authentication, password hashing/reset and backend role restrictions | Do not replace auth or weaken token/session validation |
| Tenant and audit | Tenant-aware platform records and audit activity | Preserve tenant predicates and audit semantics on every new endpoint |
| Exam setup | Exam create/read/update/publish, scheduling and state management | Extend fields and workflows compatibly |
| Questions | MCQ question/options authoring and assignment to exams | Preserve legacy MCQ behavior while introducing richer types |
| Candidate assignment | Assign by email, join by exam code, revoke assignments | Preserve eligibility and authorization checks |
| Attempts | Start/read/save/submit, persisted responses, server-side expiry validation, idempotent submit | Extend response schema without duplicate or lossy migrations |
| Candidate runner | Question display/navigation, answer indicators, timer and immediate save for current MCQ flow | Enhance in place; preserve existing route and proctoring startup |
| Proctoring | Camera/audio/browser signals, event handling, evidence and risk scores | Do not remove or conflate with academic grading |
| Reports | Existing proctoring PDF report generation and secure download | Add academic reports as a distinct report type |
| Operations | Setup scripts, health/metrics, quality checks, SQL backup helpers | Preserve operational scripts and documented setup |

## Existing source locations to inspect

These are baseline pointers, not a claim that every relevant file is listed:

- Exam services: `services/exam_service.py`
- Identity: `services/identity_service.py`
- Persistence: `database/platform_repository.py`, `database/student_repository.py`, `database/db_connection.py`
- Migrations: `database/schema_migrations.py`
- API: `infrastructure/api/fastapi_app.py`, `infrastructure/api/routers/exams.py`, `infrastructure/api/routers/attempts.py`, `infrastructure/api/routers/identity.py`
- Candidate UI: `frontend/src/routes/exam.tsx`, `frontend/src/routes/setup.tsx`
- Examiner/admin/report UI: `frontend/src/routes/instructor.tsx`, `frontend/src/routes/admin.tsx`, `frontend/src/routes/reports.tsx`
- Frontend contracts: `frontend/src/lib/api.ts`, `frontend/src/lib/queries.ts`, `frontend/src/lib/types.ts`
- Security and monitoring: `core/security.py`, `core/events/`, `core/risk/`, `monitoring/`, `browser_guard_extension/`
- Tests: `tests/` plus CI and scripts.

## Gaps observed in the inspected baseline — re-verify in Phase 0

The following were observed in the source inspection that informed this handoff. Confirm each item in the live working tree before implementation; do not rely on the list as a substitute for code review.

1. Question validation supports only `mcq`; multiple-select and written-response flows are not present end-to-end.
2. Attempt response contracts and persistence are centered on a single `selected_option_id` plus optional text, not a set of selected options with defined marking rules.
3. The current response persistence calculates objective correctness/awarded marks during save for the legacy one-option flow; this needs a grading model that supports manual written marking without publishing incomplete scores.
4. Attempt questions are read from the current exam question list rather than a full immutable per-attempt question/choice/mark-scheme snapshot.
5. Expiry is derived from start time plus exam duration in the observed path; new attempts need a persisted server-authoritative immutable deadline.
6. Candidate runner lacks marked-for-review state, multi-select controls and written-response controls in the observed route.
7. Candidate runner did not have a complete offline queue / network save-sync status workflow in the observed route.
8. No exam-scoped announcements workflow was verified in the inspected routes/API.
9. No clearly separate academic result publication/manual grading workflow was verified; existing PDF reports are primarily proctoring/risk/evidence reports.
10. No examiner sandbox isolation, structured bulk CSV/JSON imports, report authenticity verification or dedicated in-exam scratchpad was verified.
11. Existing `use-density` preference is a global density primitive, not a complete candidate examination workspace preference workflow.
12. Existing monitoring signals and risk scores are not proof of misconduct; any candidate-facing and examiner-facing copy must preserve that distinction.

## Existing route behavior to preserve

The inspected API included exam CRUD/publish/question/options/assignment endpoints, student exam listing/join-code, attempt start/read/response-save/submit, attendance and exam-attempt review. Preserve existing API contracts or extend them compatibly. The live implementation must be inspected to capture exact route schemas and permission dependencies.

## Current CI status is not a release guarantee

A previously observed GitHub Actions run passed Python compile/regression checks, frontend typecheck and production build for the baseline revision. It does not prove Nigran 360 meets the problem statement. Run all current checks after every phase and inspect the current CI workflow.

## Required Phase 0 outputs

- Actual repository/branch/commit/worktree report.
- Baseline test commands and results.
- Existing user workflows and route/API inventory.
- Database table/constraint/index and migration inventory.
- Question/response/attempt/result domain model assessment.
- Backwards-compatibility plan for old MCQ exams and attempts.
- Proposed snapshot, deadline, grading-state, publication-state and sandbox-isolation design.
- Phase dependency map, risk register and files likely to change.
- Explicit no-go list of files/behaviors that should not be touched without a reason.
