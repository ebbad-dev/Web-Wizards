# Phase 3 Prompt — Candidate Examination Workspace

Read the master prompt and all supporting docs, plus approved Phase 2 report. Execute **Phase 3 only**.

## Objective

Make the candidate runner a complete and understandable examination workspace while preserving current autosave, timer, question rendering and proctoring integration.

## Scope

1. Support all question types already delivered in Phase 1.
2. Add question states: unanswered, answered, marked for review, answered and marked for review.
3. Add mark/unmark-for-review controls and persist the state per attempt/question.
4. Add question navigation and a final review screen showing answered/unanswered/review counts and a path to each question.
5. Show question marks and remaining time clearly. Server time/deadline remains authoritative; client timer is display only.
6. Add meaningful candidate preferences (for example comfortable/compact density and readable text scale) and persist them. Reuse existing density preference if appropriate; do not let preferences hide controls or status.
7. Add an in-exam digital scratchpad that is scoped to candidate and attempt, usable by keyboard and screen reader, and excluded from grading and examiner-visible data by default.
8. Keep scratchpad persistence minimal and documented; clear/expire according to a safe policy after completion or retention period.
9. Add loading, empty, disabled, validation and save-error states without changing the current monitoring startup flow.

## Compatibility constraints

- Preserve existing `/exam` route/query and attempt response contracts where possible.
- Preserve current proctor startup, browser guard token lifecycle and event fallback hooks.
- Do not make scratchpad text part of response payloads or grade calculation.
- Do not make local preferences a security or timing control.
- Do not allow a question review marker to affect answer scoring.

## Acceptance gate

- Four question states display accurately and survive refresh.
- Navigation and final review reflect current saved/pending status accurately.
- Every question type is usable.
- Preferences persist and remain accessible.
- Scratchpad is isolated and excluded from grading/results.
- Existing proctoring startup and attempt submission still work.
- Targeted, regression, frontend typecheck and build pass. Complete report and stop before Phase 4.
