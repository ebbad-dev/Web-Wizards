# NIGRAN-360 — Team Work Allocation

Both members are full-stack developers working across frontend and backend.

## Member A — Administration & Examiner Modules

### Backend
- Authentication APIs (login, JWT, password hashing)
- User management (CRUD, role assignment)
- Examination CRUD and lifecycle management
- Question bank (create, edit, categories, difficulty)
- ExamQuestion assignment and randomization
- Bulk import (CSV/JSON parsing and validation)
- Examination sandbox mode
- Monitoring APIs (active attempts, events)
- Announcement APIs
- Auto-grading engine (MCQ, multi-select)
- Manual grading endpoints
- Question analytics
- Examiner-side dispute review (status updates, decisions)
- PDF report generation (ReportLab)

### Frontend
- Admin dashboard (user management UI)
- Examiner dashboard
- Exam creation and configuration forms
- Question bank UI
- Question assignment and ordering
- Bulk import UI with error display
- Sandbox preview trigger
- Monitoring dashboard (live attempt view)
- Announcement form
- Manual grading interface
- Examiner dispute review UI

## Member B — Candidate & Assessment Modules

### Backend
- Candidate enrollment endpoints
- Attempt creation with server-authoritative deadline
- Answer autosave endpoint (idempotent upsert)
- Attempt recovery (resume from DB state)
- Network event logging
- Candidate-side dispute submission endpoint
- Candidate results API
- Report verification endpoint (QR code lookup)
- Scratchpad persistence (stored per attempt)
- Candidate workspace preferences (stored per user)

### Frontend
- Candidate dashboard (available, upcoming, completed exams)
- Exam entry flow and eligibility check
- Examination workspace (questions, timer, navigation)
- Answer state management (answered/unanswered/marked)
- Timer component (counts down from server deadline)
- Answer autosave with confirmation indicator
- Network status banner
- Digital scratchpad panel
- Workspace preference controls (font size, layout, theme)
- Candidate results page
- Dispute submission form and tracking UI
- QR code verification page
- Candidate PDF download

## Shared
- Architecture and database schema design
- Authentication contracts and middleware
- API contract definitions
- Database migrations (Member A coordinates)
- Integration testing
- Security review
- Deployment configuration
- README and test credentials

## Outstanding Shared Decision: D3 — Attempt Duplicate Constraint

The `Attempt` model currently has no database uniqueness constraint on `(exam_id, candidate_id)`.

The correct constraint depends on the exam retake policy, which has not yet been agreed:

- If retakes are never permitted → `UniqueConstraint("exam_id", "candidate_id")` on the Attempt table.
- If retakes are permitted but concurrent active attempts must be blocked → partial unique index filtered on `status = 'in_progress'`.
- If unlimited retakes are allowed with no DB enforcement → application-layer validation only.

**Member B must confirm the retake / concurrency policy before the Phase 4 attempt engine is integrated.**
Member A will add the agreed constraint to the migration once policy is confirmed.

Until this is resolved, `docs/security.md` does not claim a database-level duplicate attempt constraint exists.
