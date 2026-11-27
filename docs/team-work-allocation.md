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
