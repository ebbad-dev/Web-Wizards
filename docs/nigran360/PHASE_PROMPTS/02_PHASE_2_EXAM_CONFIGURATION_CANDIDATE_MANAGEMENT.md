# Phase 2 Prompt — Exam Configuration, Lifecycle and Candidate Management

Read the master prompt and all supporting docs, then the approved Phase 1 report. Execute **Phase 2 only**.

## Objective

Complete the examiner exam-setup workflow and the candidate's view of available, upcoming and completed examinations while preserving existing exam status/data semantics.

## Scope

1. Add/complete exam instructions as a first-class field with safe validation and candidate-facing display.
2. Provide examiner review/preview before publication, showing the candidate-safe exam view.
3. Validate title, schedule, duration, total marks, assigned questions, question-type configuration and candidate access before publish.
4. Map existing stored lifecycle states to required user-visible states: draft, published, upcoming, ongoing and completed. Preserve current scheduled/closed/archived semantics; do not rename/drop stored statuses casually.
5. Improve candidate enrollment details and examiner visibility of assigned/eligible candidates.
6. Build a candidate dashboard grouped into available, upcoming and completed examinations, with instructions/access status.
7. Enforce assignment, revocation, ownership, tenant and schedule rules on backend.

## Compatibility constraints

- Existing exam CRUD, publish and assignment endpoints must remain functional.
- Existing exam status strings and migration assumptions must be discovered in Phase 0 and retained/adapted.
- Do not loosen candidate assignment requirements.
- Do not reveal exams outside the user's authorized tenant/scope.
- Do not change attempt timing or question snapshot logic from Phase 1.

## Acceptance gate

- Examiner can create, preview, edit and publish a valid exam.
- Invalid/incomplete exam cannot publish and receives actionable errors.
- Candidate sees accurate available/upcoming/completed groupings.
- Candidate cannot access an unpublished, unassigned, revoked or out-of-window exam.
- Legacy exams remain visible and operate according to existing semantics.
- Role and tenant negative tests pass. Complete phase report and stop before Phase 3.
