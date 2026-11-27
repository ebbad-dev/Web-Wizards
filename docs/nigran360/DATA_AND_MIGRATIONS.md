# Data Model and Migration Strategy — Nigran 360

## 1. Guiding rule

The existing database contains real application state. Migrations must be additive, ordered, repeatable according to current migration conventions, tenant-safe and tested against SQL Server. Do not drop or rename existing columns/tables as a shortcut. Never assume a development database can be discarded.

Before any DDL, inspect:

- `database/schema_migrations.py`
- actual SQL DDL / schema initialization
- repository SQL queries and indexes
- foreign keys, unique constraints, defaults and nullability
- existing data distributions and legacy values
- backup/restore scripts and SQL Server smoke tests

## 2. Conceptual target entities

The final physical schema must be designed from the live database in Phase 0. These are conceptual boundaries, not mandatory table names.

### Question bank item

- stable question ID and tenant/owner scope
- type: legacy-compatible single choice, multiple select or written response
- question text and safe rendering metadata
- category/topic and difficulty
- maximum marks
- type-specific marking configuration/version
- lifecycle/active metadata and audit timestamps

### Question options

- stable option ID
- parent question ID
- option text and display metadata
- correctness data stored only server-side
- ordering metadata

### Exam question assignment

- exam ID and question ID or immutable question version
- exam-specific marks/order/settings if allowed
- randomization policy
- validation that total marks match configured exam total or documented scheme

### Attempt

- attempt ID, exam ID, assignment/candidate/user IDs and tenant scope
- status, start/submit/expiry timestamps
- immutable `deadline_at` for new attempts
- attempt type/discriminator: real or sandbox
- question snapshot/version reference
- submission/idempotency metadata
- grading status and published/result state as appropriate

### Attempt question snapshot

For every question assigned to an attempt, preserve:

- frozen question content and type
- question order
- maximum marks
- frozen marking scheme/version
- frozen options and option order where applicable
- correctness data server-side only

Choose normalized relational snapshot tables or a validated immutable JSON snapshot, based on existing SQL conventions and query requirements. If JSON is used, validate schema/version and keep answer-key data out of candidate responses. A hybrid model may be appropriate.

### Response

Represent all supported answer forms without discarding legacy data:

- single selected option ID
- selected option ID collection for multiple select
- written text
- response version / idempotency ID
- server accepted timestamp
- status and grading result (objective result vs pending manual)
- awarded marks and optional grader metadata

A normalized response table plus a validated JSON payload may be preferable to repeated schema rewrites; decide during Phase 0. Keep legacy `selected_option_id`, `response_text`, `is_correct` and `awarded_marks` semantics readable where they exist. Do not store a multiple-select list as comma-separated text.

### Manual grade

- response/question/attempt reference
- awarded marks constrained to the question maximum
- examiner ID
- feedback if supported
- grading version/status
- created/updated timestamp and audit trail

### Result publication

- exam/result-set publication state
- published timestamp and publisher ID
- optional version/reissue metadata
- visibility policy

### Announcements

- exam ID and tenant/owner scope
- body/title and priority/visibility if needed
- created by, timestamps and target state
- optional expiration

### Import batch

- source type and uploader
- validation status and counts
- safe file metadata (not necessarily retained raw file)
- row-level error summary
- transaction outcome and created record IDs

### Report verification

- report ID and cryptographically random opaque token or secure digest
- report type/version/status
- issued/revoked timestamps and issuer
- minimal verification response metadata
- no direct public exposure of marks or candidate information

## 3. Immutable attempt snapshot

This is one of the most important invariants in the product.

At attempt creation, in a single transaction:

1. Validate candidate assignment and exam window.
2. Read the published exam configuration and question versions.
3. Resolve random question and option ordering once.
4. Copy/freeze question content, marks and marking scheme into the attempt snapshot.
5. Create attempt with server-calculated `started_at` and immutable `deadline_at = started_at + allowed duration` (or another explicitly approved policy).
6. Return a candidate-safe projection that omits correctness keys and private rubric data.

Every subsequent candidate request must read from the attempt snapshot, not the mutable reusable question bank. Editing a question or exam after start must not change the active attempt.

## 4. Legacy attempts and compatibility

- Keep legacy MCQ response fields readable.
- New code must support legacy single-choice answers through an adapter/normalizer.
- Do not attempt to reconstruct immutable question text/option order if no historical snapshot exists. For legacy attempts, preserve the existing behavior and document that their historical assignment fidelity is limited.
- For legacy attempts without `deadline_at`, derive the fallback only from the historical fields available at read/validation time (for example, start time plus the relevant duration) and document the risk if exam duration was editable. Do not invent a deadline that changes the old record's meaning.
- Never backfill a deadline using the current wall clock or a currently edited exam's duration without an explicit approved migration rule.
- Do not force manual grading for already-completed legacy MCQ attempts.

## 5. Deadline and timing

- Server UTC clock is authoritative.
- Store a deadline for each new attempt at creation.
- Do not accept answer mutations after server deadline.
- Explicit submit and expiry finalization share an idempotent transition.
- Client countdown is a display; it is not authoritative.
- Handle server/client clock skew by returning server time/deadline and displaying a countdown based on a server-time anchor.

## 6. Grading and publication state

Use explicit states rather than overloading a nullable score:

- `not_started` / `in_progress` / `submitted` / `expired` (align with current attempt state model)
- objective grading complete or pending manual grading
- examiner review required / ready for publication / published (align with current state vocabulary)

The exact enum/string values must follow existing naming conventions and migration strategy. Define all allowed transitions and guard them in service methods. Recompute totals deterministically from snapshotted question maximums and validated marks.

## 7. Sandbox isolation

Sandbox data must be structurally identifiable and must be filtered from:

- real candidate attendance
- real submissions and results
- exam completion counts
- performance reports and question analytics
- candidate-facing published results
- bulk exports and official statistics
- any production grading/review workflow

A single boolean flag is acceptable only if every query and aggregation enforces it and tests prove that. Prefer an explicit attempt type plus centralized repository filters. Never infer sandbox status from usernames, exam names or client-supplied flags.

## 8. Network queue and idempotency

- Every response mutation gets a client-generated unique idempotency key (cryptographically random UUID is acceptable) and monotonic client-side sequence within the attempt.
- Server stores/recognizes processed keys to make retries safe.
- Use response version/optimistic concurrency to prevent stale overwrites.
- A server acknowledgement is required before showing the response as saved.
- Queue size and retention must be bounded; clear local queue after confirmed submit or explicit cleanup.
- Candidate-local storage is untrusted and may contain sensitive response text. Minimize scope/retention, avoid storing secrets, and disclose behavior.
- Do not trust browser-provided time as evidence of a pre-deadline answer. Server deadline remains authoritative.

## 9. Migration safety checklist

- Migration is additive and safe on an existing database with data.
- New nullable/defaulted columns are introduced before new code depends on them.
- Backfill is deterministic, bounded and tested.
- Index creation is planned for production table size and SQL Server version.
- Referential integrity is preserved.
- Tenant columns and predicates are correct.
- Migration can be rerun or safely recognized according to project conventions.
- Backup exists and restore procedure is known before high-risk DDL.
- Old application behavior can still read old records during transition.
- Rollback plan does not depend on destructive data reversal. Prefer forward-fix for additive changes; state what would be required to roll back safely.
- Tests include a pre-migration fixture, post-migration assertions and real SQL Server smoke where possible.
