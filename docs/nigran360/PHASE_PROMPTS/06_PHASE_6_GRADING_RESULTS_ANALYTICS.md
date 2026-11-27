# Phase 6 Prompt — Evaluation, Grading, Results and Analytics

Read the master prompt, PRD, SRS, data/migrations, security and testing docs, plus approved Phase 5 report. Execute **Phase 6 only**.

## Objective

Complete reliable grading for objective and written questions, give examiners controlled result review/publication, and provide meaningful analytics from actual submissions.

## Scope

1. Implement deterministic objective grading from immutable attempt snapshots for single-choice and multiple-select questions.
2. Implement manual grading for written responses with response text, max marks, awarded marks, feedback (if approved), grader identity and timestamp.
3. Validate marks against the snapshotted question maximum. Prevent grading by candidates or unauthorized examiners.
4. Introduce explicit grading states so written answers do not silently count as zero or publish incomplete results.
5. Recalculate totals deterministically from all snapshotted questions and approved marks.
6. Add examiner grading queue/filter for pending written responses and review-ready attempts.
7. Add examiner result review and explicit publish action with audit metadata.
8. Add candidate result screen restricted to the authenticated candidate's own published results.
9. Add exam performance summary based on real submitted attempts: participation, score distribution/summary and completion counts as justified by data.
10. Add question analytics: attempts, skipped, incorrect and observed difficulty metric. State sample size and avoid overclaiming statistical precision.
11. Exclude sandbox and in-progress attempts from official summaries and results.
12. Preserve completed attempts and result history for authorized review.

## Scoring requirements

- Do not trust client-supplied score or correctness flags.
- Use the marking scheme frozen into the attempt snapshot.
- Do not add negative marking unless approved and represented in the exam config/snapshot.
- Ensure multiple-select behavior is explicitly defined and tested.
- Ensure a question with no response is treated according to the approved marking scheme, not an accidental null conversion.
- If a result has pending manual grading, mark it clearly as not ready to publish.

## Publication requirements

- Result visibility is controlled by an authorized examiner.
- Candidate endpoints must never return another candidate's result.
- Unpublished result is inaccessible even if the candidate knows an attempt ID.
- Publishing/re-publishing is idempotent and audited.

## Analytics requirements

- Use only actual completed/submitted real attempts for official analytics.
- Exclude sandbox, demo, in-progress and invalidated records.
- Include sample size and handle small samples honestly.
- Do not use proctoring risk score as an academic performance metric.

## Acceptance gate

- Objective scoring tests cover correct, incorrect, skipped and multiple-select cases.
- Manual grading permissions, score bounds and audit work.
- Result totals are correct and stable after reload.
- Unpublished results are hidden; published results are candidate-private.
- Analytics are traceable to real data and exclude sandbox/in-progress attempts.
- Existing proctoring reports are unchanged. Complete report and stop before Phase 7.
