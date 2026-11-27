# Phase 0 Prompt — Baseline, Compatibility and Technical Design

Read `MASTER_PROMPT.md` and all supporting handoff documents first. Execute **Phase 0 only**. Do not implement new product features or make schema changes in this phase.

## Objective

Establish exactly what exists in the current repository, what works, what the official requirements still need, and how the missing features can be added without breaking working behavior.

## Tasks

1. Record current repository path, branch, HEAD commit, `git status`, untracked files and all local changes. Stop if the working tree contains unrecognized work; do not clean, reset or stash it.
2. Confirm the repository and default branch. Work planning must target a dedicated feature branch, not `main`. Do not create/switch branches until safe with respect to the working tree.
3. Inventory frontend routes/components/hooks/API types; backend routers/services/schemas/repositories; database tables/columns/indexes/constraints/migrations; CI and test scripts.
4. Map existing flows: authentication, admin roles, examiner exam CRUD/publish, questions/options, assignments, candidate exam listing/join, attempt start/get/save/submit/expiry, monitoring, evidence, proctoring report and operations.
5. Run the existing baseline test/quality commands. Record exact commands, environment, result/counts and blockers. Do not change tests or code to manufacture a green baseline.
6. Verify every gap in `PROJECT_BASELINE.md` from source. Mark each `confirmed`, `not present`, `partially present` or `unknown`, with file/API/database evidence.
7. Trace current single-MCQ data from frontend payload to Pydantic model to service to SQL persistence to reload and score calculation.
8. Inspect concurrency and transaction behavior for attempt start, save and submit. Identify race conditions and current idempotency keys/constraints.
9. Inspect exam status values, publish validation, edit restrictions, question assignment rules and whether an active attempt can see mutated exam/question content.
10. Design compatible data/API contracts for: reusable question bank, all three question types, marking schemes, attempt snapshots, random ordering, immutable server deadline, answer status/review flag, auto/manual grading, result publication, sandbox discriminator, announcement records and import/report entities.
11. Design the offline queue trust model. Keep server deadline authoritative; explain why browser timestamps cannot prove that an unsynced answer was written before expiry. Do not propose a client-clock grace period as secure.
12. Create a risk register sorted by severity and a dependency graph of phases.
13. Produce a Phase 1 implementation plan with proposed file touch list, migration sequence, compatibility adapter, API contract and tests.

## Required outputs

- `docs/nigran360/PHASE_0_BASELINE_REPORT.md` or an equivalent clear report.
- Updated `PROJECT_BASELINE.md` only if facts were verified differently; preserve the handoff's intended baseline history.
- Route/API/schema/table inventory.
- Existing-vs-required feature matrix.
- Data/API compatibility design and migration plan.
- Risk register and Phase 1 execution plan.
- Phase completion report using the template.

## Acceptance gate

- No feature code changed and no database migration applied.
- Repository state and baseline tests are documented.
- Current MCQ compatibility path is understood end-to-end.
- Snapshot, deadline, grading and publication model are reviewed.
- Every unknown or untestable point is honestly recorded.
- Present the report and stop. Wait for explicit approval to begin Phase 1.
