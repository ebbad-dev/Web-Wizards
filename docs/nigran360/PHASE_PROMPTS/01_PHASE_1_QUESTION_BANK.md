# Phase 1 Prompt — Reusable Question Bank and Question Types

Read the master prompt, PRD, SRS, architecture, data/migration, security and testing documents, plus the approved Phase 0 report. Execute **Phase 1 only**.

## Objective

Upgrade the current MCQ-centric authoring model into a reusable question bank that supports single-answer MCQ, multiple-select and written-response questions with appropriate marking schemes and immutable attempt assignment snapshots.

## Scope

1. Add reusable question-bank concepts using the existing tenant/owner model.
2. Add category/topic and difficulty metadata with safe defaults for legacy questions.
3. Support three question types:
   - Single-answer MCQ (maintain legacy payload/data compatibility).
   - Multiple-select (persist a set of selected option IDs, not comma-separated strings).
   - Written response (persist validated text; manual grading comes in Phase 6).
4. Define marking-scheme representation and validation. Single-choice and multiple-select objective grading must be deterministic. Do not add negative marking unless an explicit product rule is approved. Clearly define exact-match/partial-credit behavior and test it.
5. Update examiner question builder and frontend/backend types for type-aware authoring and validation.
6. Support assigning reusable questions to exams.
7. Implement question/option randomization at attempt creation, not on every refresh.
8. Freeze question text, question type, marks, option content/order and marking scheme into an immutable attempt snapshot.
9. Keep answer keys and private marking data server-side; candidate API receives only candidate-safe snapshots.

## Compatibility requirements

- Existing MCQ exams continue to open, edit, publish and run.
- Existing `selected_option_id` responses remain readable.
- Additive SQL Server migrations only; follow approved Phase 0 design.
- Do not change unrelated role/auth/proctoring/monitoring/report behavior.
- Do not make a source question edit alter active attempt content or order.
- New written-response saves are not marked incorrect/zero merely because no objective key exists.

## Work sequence

1. Inspect approved Phase 0 files and tests.
2. Add migration and compatibility/read adapters.
3. Implement backend validation and service/repository operations.
4. Add API contract and candidate-safe serialization.
5. Implement question-bank UI and type-aware builder with clear validation.
6. Update frontend types/API hooks without broad UI refactoring.
7. Add tests for legacy MCQ, multiple-select, written text, marking configuration, randomization, snapshot immutability, unauthorized access and answer-key leakage.
8. Run full regression, migration tests and SQL Server smoke where available.

## Acceptance gate

- All three question types can be created, edited, assigned and displayed correctly.
- Existing MCQ behavior remains unchanged for legacy records.
- Randomized assignment is stable within an attempt.
- Active attempt snapshot is unaffected by later source question edits.
- Candidate responses never expose answer keys.
- Backend validations reject invalid option IDs, invalid marks and malformed types.
- Tests and Phase 1 completion report are complete. Stop before Phase 2.
