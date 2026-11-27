# Implementation Plan — Nigran 360

## 1. Execution policy

Execute one phase at a time. Phase 0 is mandatory. A phase is complete only after its acceptance tests, regression checks, documentation and phase report are complete. Do not start a dependent phase while a blocking issue remains.

## 2. Dependency sequence

```text
Phase 0 Baseline and compatibility design
   ↓
Phase 1 Question bank, types, marking scheme and attempt snapshot
   ↓
Phase 2 Exam lifecycle, instructions and candidate management
   ↓
Phase 3 Candidate workspace, review states, preferences and scratchpad
   ↓
Phase 4 Network-aware sync and failure-resilient behavior
   ↓
Phase 5 Monitoring progress and announcements
   ↓
Phase 6 Grading, result publication and analytics
   ↓
Phase 7 PDF, sandbox, imports and report verification
   ↓
Phase 8 Integration, security, reliability, demo and submission readiness
```

Some features depend on more than one phase; the detailed requirements traceability appears below.

## 3. Phase summary and gates

| Phase | Deliverable | Primary gate |
|---|---|---|
| 0 | Verified baseline, dependency map, safe data/API design | No feature changes; design and risks reviewed |
| 1 | Reusable question bank and three supported question types | Legacy MCQ regression passes; snapshots immutable |
| 2 | Complete exam setup/review/lifecycle and candidate exam dashboard | Eligibility, schedule and role boundaries pass |
| 3 | Complete candidate runner workspace | Review, preferences and scratchpad preserve attempt behavior |
| 4 | Visible save/sync state and resilient retry/resume | No false saved state, duplicate writes or extra time |
| 5 | Examiner monitoring and candidate announcements | Ownership, audience scoping and human review pass |
| 6 | Objective/manual grading, results and analytics | Accurate scores and controlled publication pass |
| 7 | Four remaining secondary features | Isolation, imports, PDF authorization and verification pass |
| 8 | Full system verification and demo readiness | All available checks pass and cutoff is respected |

## 4. Phase 0 — inspect and design

- Verify repository head, branch and dirty state.
- Run current tests before changes.
- Map route → service → repository → table flow.
- Inventory existing auth, role, tenant and audit policies.
- Inventory questions, options, exam assignments, attempts, responses, scoring, reports and migrations.
- Verify gaps and all baseline assumptions in `PROJECT_BASELINE.md`.
- Design compatible response union, marking scheme, attempt snapshot, immutable deadline, manual grading state, publication state and sandbox discriminator.
- Produce a risk register and test plan.
- Stop before product code changes.

## 5. Phase 1 — question bank and types

Backend: type-aware schemas and validation, reusable question metadata, marking scheme representation, randomization and immutable snapshot creation. Database: additive migrations. Frontend: question bank UI and type-aware builder. Tests: old MCQ behavior, multi-select and written persistence, answer-key confidentiality, snapshot stability.

## 6. Phase 2 — exam and candidate lifecycle

Add instructions and examiner review/preview. Reconcile required lifecycle presentation with existing persisted states. Improve candidate enrollment and dashboard. Tests must prove no premature access and no cross-user/exam leakage.

## 7. Phase 3 — candidate workspace

Add review state and navigation/final review, preferences, scratchpad. Persist review state as attempt metadata or per-question state using the reviewed model. Keep the existing exam runner's proctoring startup and timer. Keep scratchpad isolated and not part of official response/grading data.

## 8. Phase 4 — failure-resilient workflow

Add browser online/offline listeners, save-state UI, bounded IndexedDB/local queue, idempotency and response versioning. Reconnect through normal server authorization/deadline validation. Make the server deadline immutable and authoritative. Do not stop or reset timers on connectivity changes. Test refresh, reconnect, repeated requests, stale writes and expiry while offline.

## 9. Phase 5 — monitor and communicate

Add examiner progress view and exam announcement records/delivery. Reuse existing monitoring events. Ensure risk/incident data remains contextual and reviewable. Use existing polling/query patterns unless current project has a suitable realtime abstraction.

## 10. Phase 6 — grading, release and analytics

Separate auto grading from manual written grading. Add examiner marking, mark validation and audit. Calculate totals deterministically. Add review-ready and published states. Add candidate-safe result screen. Add exam-level and per-question analytics derived only from real submitted attempts.

## 11. Phase 7 — secondary features

- Academic performance PDF, independent of existing proctoring PDFs.
- Isolated examiner sandbox.
- CSV/JSON question and candidate imports with preview, validation and safe transaction.
- Verifiable report token/QR with minimal public verification.

Re-run all previously implemented secondary feature tests, not just the new Phase 7 tests.

## 12. Phase 8 — final verification

Run end-to-end role journeys, regression, schema migration, SQL Server smoke, frontend typecheck/build, security checks, import/file validation, sandbox exclusion checks, PDF authorization, accessibility/responsive checks and failure simulations. Update README and demo instructions. Rehearse with synthetic users/data. Check the official deadline before any commit/push/build/deployment. Do not perform prohibited actions after cutoff.

## 13. Stop conditions

Stop the phase and report instead of continuing when:

- repository is dirty or contains unknown changes;
- baseline tests are failing for an unrelated or unclear reason;
- migration could destroy/alter existing data without backup and compatibility plan;
- new behavior would weaken authorization or tenant isolation;
- existing MCQ/attempt behavior would break;
- the deadline/fairness design depends on untrusted client time;
- the feature cannot be tested in the available environment;
- a required product decision is unresolved and materially changes data/API behavior.

## 14. Traceability matrix

| Official requirement | Phase | Proof expected |
|---|---:|---|
| 3.1 Authentication & authorization | 0–8 | Backend role, ownership and tenant negative tests |
| 3.2 Examination management | 2 | Configure, preview, publish and lifecycle tests |
| 3.3 Question management | 1 | Question types, marking scheme, randomization, snapshots |
| 3.4 Candidate management | 2 | Enrollment, candidate dashboard and eligibility tests |
| 3.5 Examination interface | 3–4 | Navigation, statuses, save/reload/expiry tests |
| 3.6 Examination monitoring | 5 | Live progress, events and announcements tests |
| 3.7 Evaluation & grading | 6 | Objective and manual grading tests |
| 3.8 Results & analytics | 6 | Review, publish, candidate visibility and analytics tests |
| 4.1 Network-aware interface | 4 | Offline/online/save state tests |
| 4.2 PDF reports | 7 | Authorized academic report generated from real performance data |
| 4.3 Sandbox | 7 | Exclusion tests for real totals/reports/results |
| 4.4 Bulk import | 7 | CSV/JSON validation/preview/transaction tests |
| 4.5 Question analytics | 6 | Skipped/incorrect/difficulty aggregates |
| 4.6 Verifiable reports | 7 | QR/ID verification and privacy tests |
| 4.7 Customizable workspace | 3 | Persisted preferences and UI behavior tests |
| 4.8 Digital scratchpad | 3 | Candidate/attempt scope and grading exclusion tests |
| 5.3 Failure-resilient examinations | 4, 8 | Demonstration and no-extra-time server enforcement |
