# Software Requirements Specification — Nigran 360

## 1. System context

Nigran 360 extends the existing ProctorAI application. The browser frontend communicates with a FastAPI backend. The backend uses the existing SQL Server persistence layer and existing authentication, audit, tenant and proctoring infrastructure. The candidate exam runner remains integrated with the current monitored-session startup and browser guard behavior.

## 2. Roles and authorization

**Terminology compatibility:** The competition uses Administrator, Examiner and Candidate. The existing codebase appears to use internal `admin`, `instructor` and `student` roles. Verify this in Phase 0 and map labels/experiences without renaming stored role values or weakening current privilege rules. A role migration requires a separate compatibility design and tests.

| Capability | Administrator | Examiner | Candidate |
|---|---:|---:|---:|
| Manage platform users/roles | Yes | No | No |
| Create/manage own authorized exams | Only where current admin policy permits | Yes | No |
| Manage question bank | Authorized platform scope | Own/authorized scope | No |
| Enroll candidates | Authorized scope | Own/authorized exams | No |
| View assigned exam instructions | If authorized | Yes | Yes, for assigned exams |
| Start/save/submit attempt | No candidate impersonation by default | Sandbox only | Own eligible attempt |
| Monitor live attempts | Authorized admin scope | Own/authorized exam | Own status only |
| Review proctoring incidents | Authorized scope | Own/authorized exam | Only appropriate disclosed status; not raw examiner notes |
| Grade written answers | No, unless existing role policy explicitly includes examiner privileges | Yes | No |
| Publish results | Authorized policy | Own/authorized exam | No |
| View results | Authorized scope | Own/authorized exam | Own published results only |
| Import candidates/questions | Authorized scope | Own/authorized exam/bank | No |
| Generate/download academic reports | Authorized scope | Own/authorized exam | Own permitted report only |
| Verify report token | Public minimal verification response | Yes | Yes |

Every row must be enforced by backend authorization and tenant/ownership checks. Frontend hiding is not an access control.

## 3. Functional requirements

### FR-01 Authentication and authorization (official 3.1)

- Preserve secure authentication for administrators, examiners and candidates.
- Preserve admin user/role management.
- Enforce role, tenant, exam ownership, candidate assignment and object-level access on the backend.
- Reject unauthorized and cross-tenant requests with safe errors.
- Do not expose secrets, password hashes, session tokens or grading keys.

### FR-02 Examination configuration and lifecycle (official 3.2)

- Examiners can create exams with title, instructions, schedule, duration, total marks and relevant settings.
- Support draft and publication workflows, plus user-visible upcoming/ongoing/completed states.
- Preserve existing persisted status values and semantics unless a reviewed migration is required.
- Examiners can review the candidate-facing exam before publication.
- Candidates cannot enter before availability or outside the authorized window.

### FR-03 Question bank and question model (official 3.3)

- Provide reusable question records with category/topic and difficulty metadata.
- Support `single_choice` (legacy MCQ-compatible), `multiple_select` and `written_response`.
- Each question has validated marks and a configured marking scheme appropriate to its type.
- Objective questions and/or choices may be randomized where enabled.
- Candidate-facing APIs must not expose correctness data before authorized result release.
- An active attempt must use an immutable snapshot of assigned question content, question order, option order and marking scheme.
- Existing MCQ records must migrate/read with a compatibility adapter or safe default.

### FR-04 Candidate management and dashboard (official 3.4)

- Examiners can enroll eligible candidates and inspect enrollment information.
- Candidates can see available, upcoming and completed exams with instructions and access status.
- Backend enforces assignment, revocation, exam ownership and availability window.
- Do not leak other candidates' identities or assignment details.

### FR-05 Examination workspace and attempts (official 3.5)

- Show question content, marks, remaining time and navigation.
- Represent states: unanswered, answered, marked-for-review, answered-and-marked-for-review.
- Autosave answers and show save status.
- Preserve server-acknowledged progress after refresh/re-entry.
- Support candidate progress review before submission.
- Enforce the immutable server deadline; finalize once on expiry using only accepted responses.
- Preserve idempotent submission behavior.
- Persist attempt snapshots and a server-calculated immutable `deadline_at` for new attempts.

### FR-06 Monitoring and announcements (official 3.6)

- Examiners can view active attempt state and meaningful progress.
- Examiners can see relevant monitoring events/incidents scoped to their exams.
- Examiners can create exam-scoped announcements for eligible candidates.
- Candidates can see relevant announcements in the exam workflow.
- Incidents are review indicators, not conclusive evidence of misconduct. No automatic guilt finding or grade penalty from risk score alone.

### FR-07 Evaluation and grading (official 3.7)

- Objective responses are graded against the snapshotted marking scheme.
- Multiple-select marking follows a clearly defined configured rule and is covered by unit tests.
- Written responses enter a pending-manual-grading state.
- Authorized examiners can assign marks within `[0, question.max_marks]` and optionally record feedback.
- Regrading is auditable and must not corrupt prior grade state.
- Exam totals are calculated from the attempt's snapshotted question marks and valid awarded marks.
- Results remain unpublished until explicit examiner review and publication.

### FR-08 Results and analytics (official 3.8)

- Examiners can review results before publication.
- An authorized examiner can publish results for an exam; publication is auditable and controlled.
- Candidates can view only their own published results.
- Provide exam-level performance summaries based on actual submitted attempts.
- Retain completed attempts and results for authorized review.
- Question analytics include skipped rate, incorrect response patterns and an observed difficulty indicator based on real submitted attempts.
- Exclude sandbox and in-progress attempts from official results/analytics.

### FR-09 Network-aware interface (secondary 4.1)

- Detect browser connectivity changes and communicate online/offline state.
- Display per-answer save state and pending synchronization count.
- Retry transient failures safely using stable idempotency identifiers.
- Do not show an answer as saved until the server acknowledges it.
- Handle conflicts deterministically and explain unresolved errors.

### FR-10 Academic PDF reports (secondary 4.2)

- Generate readable PDF reports from actual exam/candidate performance data.
- Apply role and ownership restrictions to report creation and download.
- Keep academic reports separate from existing proctoring risk/evidence PDFs.
- Do not include unnecessary PII or private evidence.

### FR-11 Examination sandbox (secondary 4.3)

- Examiners can preview an exam as a candidate.
- Sandbox attempts must be structurally isolated or clearly tagged and excluded from real submissions, attendance, grading, results, exports and analytics.
- Sandbox must not send real candidate notifications or trigger real proctoring/disciplinary workflows unless explicitly separated and approved.

### FR-12 Bulk data import (secondary 4.4)

- Import candidate records and question records from CSV or JSON.
- Validate schema, field types, required fields, duplicates, question options, correct-answer configuration and marks.
- Provide a preview/validation report and clear row-level errors.
- Use safe transaction semantics; default to no partial writes when validation fails unless the UI clearly communicates an explicitly chosen partial-import mode.
- Enforce authorization, file size/row limits and safe parsing.
- Never allow imported plaintext passwords or arbitrary code execution.

### FR-13 Question analytics (secondary 4.5)

- For each question, report attempt count, skipped count/rate, incorrect count/rate and an observed difficulty indicator.
- State the sample size and avoid overinterpreting small samples.
- Do not expose candidate identity in aggregate views unless specifically authorized and necessary.

### FR-14 Verifiable reports (secondary 4.6)

- Each issued report has a unique, unguessable verification identifier or QR token.
- Public verification returns minimal authenticity/status information and does not expose unnecessary candidate PII, marks or evidence.
- Token generation/storage/verification must use cryptographically secure identifiers or signatures and resist enumeration.
- Revocation/reissue must be auditable.

### FR-15 Customizable workspace (secondary 4.7)

- Candidates can change meaningful layout/view preferences, such as density or readable text scale, without altering exam content or available time.
- Preferences persist for the candidate according to the selected storage strategy.
- Preferences must remain accessible and not hide required controls or status information.

### FR-16 Digital scratchpad (secondary 4.8)

- Provide a usable rough-work area inside the exam workflow.
- Scope notes to the candidate and attempt; do not include them in grading or examiner-visible data by default.
- Preserve notes during the attempt and refresh according to a documented local persistence policy.
- Clear or expire notes according to a disclosed retention policy.

### FR-17 Failure-resilient innovation (official 5.3)

- Reduce answer loss caused by temporary network interruption, refresh and supported device recovery.
- Use the original server deadline; connectivity loss does not automatically pause or extend exam time.
- Queue answer changes locally only while clearly labelled pending and retry safely.
- On return, restore server-acknowledged state and reconcile pending writes only while accepted by server policy.
- Do not treat untrusted browser timestamps as proof that an answer was composed before expiry.
- Provide a demonstrable failure/reconnect scenario and explain limitations honestly.

## 4. Non-functional requirements

### NFR-01 Security

Server-side RBAC and object-level authorization; tenant isolation; secure password/token handling; parameterized SQL; input validation; least privilege; secret hygiene; safe file handling; protected report endpoints; audit coverage.

### NFR-02 Data integrity

Transactional answer and grade persistence; idempotent requests; unique constraints where appropriate; immutable attempt snapshot; immutable deadline; duplicate submission protection; correct score calculation.

### NFR-03 Reliability

Graceful handling of refreshes, repeated clicks, request timeouts, interrupted saves, duplicate retries and partial service failures. No false success states.

### NFR-04 Maintainability

Use existing service/repository/API separation. Avoid large route modules and duplicated business rules. Use typed request/response schemas and focused tests.

### NFR-05 Performance

Avoid loading all candidates, questions, events or evidence into one unbounded request. Paginate large examiner views, bound import sizes, and calculate analytics with indexed queries or appropriate aggregation.

### NFR-06 Accessibility and usability

Keyboard operability, visible focus, labels, semantic controls, contrast, responsive layouts, screen-reader-readable statuses, clear error/help text and no reliance on color alone.

### NFR-07 Privacy

Minimal data collection/return, limited scratchpad retention, protected candidate records and no unnecessary raw evidence in academic reports.

### NFR-08 Portability and constraints

Continue to work with the repository's documented Windows/SQL Server development environment and no paid API or billing-dependent service.

## 5. Data and domain invariants

1. An attempt's question/option/order/marking snapshot is immutable after it begins.
2. A response belongs to one attempt and one snapshotted question.
3. A candidate can mutate only their own active attempt before server deadline.
4. A submitted/expired attempt cannot accept arbitrary new answers.
5. A response retry with the same idempotency key must not duplicate state or scoring.
6. Objective score calculation is deterministic and repeatable.
7. Manual marks are bounded and auditable.
8. A result cannot become candidate-visible before release.
9. Sandbox data never contaminates real records or analytics.
10. Tenant and role constraints apply to every read/write/export/verification path.

## 6. Requirement-to-phase matrix

| Requirement | Phase |
|---|---|
| 3.1 | Protect in every phase; Phase 8 security verification |
| 3.2 | 2 |
| 3.3 | 1 |
| 3.4 | 2 |
| 3.5 | 3 and 4 |
| 3.6 | 5 |
| 3.7 | 6 |
| 3.8 | 6 |
| 4.1 | 4 |
| 4.2 | 7 |
| 4.3 | 7 |
| 4.4 | 7 |
| 4.5 | 6 |
| 4.6 | 7 |
| 4.7 | 3 |
| 4.8 | 3 |
| 5.3 | 4, validated in 8 |
