# Product Requirements Document — Nigran 360

## 1. Product overview

**Nigran 360** is a full-stack examination management platform for institutions and competition organizers. It supports examination creation, secure candidate access, exam delivery, monitoring, evaluation, result publication and performance reporting. It evolves an existing ProctorAI codebase, reusing the current proctoring and platform foundations.

## 2. Problem statement

Online examinations must coordinate people, exam content, timing, answer persistence, monitoring, grading and result release. They are vulnerable to unfair access, data loss during network interruptions, weak grading workflows, inconsistent question assignment and poor visibility for candidates and examiners. Nigran 360 must address the entire examination lifecycle rather than only presenting questions in a browser.

## 3. Users and goals

### Administrator

- Securely manage user accounts and role assignments.
- Control platform access and operations.
- Review audit/operational information within authorized scope.

### Examiner

- Build and reuse questions.
- Configure, preview and publish examinations.
- Enroll candidates and view eligibility/status.
- Monitor active attempts and communicate announcements.
- Review incidents without treating automated indicators as proof.
- Grade written answers, review totals and publish results deliberately.
- Analyze candidate and question performance.

### Candidate

- See available, upcoming and completed assigned examinations.
- Understand instructions and access status.
- Complete a clear, accessible timed examination.
- Save and recover progress safely when ordinary network issues occur.
- Mark questions for review, use a scratchpad and configure workspace preferences.
- Submit and view only their own published results.

## 4. Product principles

1. **Preserve the working foundation:** extend the current system; do not rewrite it.
2. **Server authority:** authorization, deadlines, grading, publication and data integrity are enforced on the backend.
3. **Immutable attempts:** a candidate's assigned questions, option order and marking scheme cannot drift during an attempt.
4. **No silent failure:** candidates see whether answers are pending, saving, saved or failed.
5. **Fairness over convenience:** recovery must not grant unverified extra exam time.
6. **Human review:** proctoring and integrity indicators support review; they do not convict candidates.
7. **Privacy by design:** expose only the information required for a workflow.
8. **Integrated UX:** features should form one coherent product with clear navigation and accessible interaction.

## 5. Scope

### In scope

- Role-based authentication and authorization (preserve current foundation).
- Full exam lifecycle and examiner review before publication.
- Reusable question bank with categories/topics, difficulty, supported question types and marking schemes.
- Candidate enrollment, eligibility and exam dashboard.
- Immutable attempt snapshots and server-authoritative deadlines.
- Timed exam UI, answer autosave, review flags, progress summary and submit.
- Connectivity/save/sync status and bounded recovery queue.
- Existing monitoring plus examiner active-attempt visibility and exam announcements.
- Automatic objective grading and manual written-answer grading.
- Controlled result publication and exam/question analytics.
- All eight secondary features (implemented across phases).
- Failure-resilient examination as the selected innovation challenge.
- Test data, setup documentation, test-role credentials via safe setup and a 15-minute demo plan.

### Out of scope unless separately approved

- Replacing the entire stack or migrating away from SQL Server.
- A new AI model/service as the core integrity solution.
- Paid APIs, paid keys, billing-dependent services, proprietary datasets or specialized hardware.
- Treating browser-side telemetry as definitive proof of misconduct.
- Rebuilding existing authentication, camera/audio monitoring or proctoring PDF reporting.
- Full LMS capabilities such as course authoring, attendance unrelated to exams, tuition/payment or gradebook integrations.
- A distributed microservice architecture or a new event broker without demonstrated need.

## 6. Feature roadmap

| Phase | Feature set | Official mapping |
|---|---|---|
| 0 | Baseline, compatibility design, migration plan | Technical reliability prerequisite |
| 1 | Reusable question bank, categories/topics, difficulty, MCQ/multi-select/written, marking schemes, randomization and snapshots | 3.3 |
| 2 | Exam instructions, lifecycle/review, enrollment visibility, candidate dashboard | 3.2, 3.4 |
| 3 | Exam runner states, mark-for-review, final review, workspace preferences, scratchpad | 3.5, 4.7, 4.8 |
| 4 | Connectivity/save/sync states, local queue, safe resume | 4.1, 5.3 |
| 5 | Active monitoring progress, incident review and announcements | 3.6 |
| 6 | Objective/manual grading, publication, candidate results, performance/question analytics | 3.7, 3.8, 4.5 |
| 7 | Academic PDFs, sandbox, CSV/JSON bulk import, report verification | 4.2, 4.3, 4.4, 4.6 |
| 8 | Integrated hardening, demo and submission readiness | All requirements / quality |

## 7. Core workflows

### Examiner workflow

1. Create or select reusable questions.
2. Build an exam, set instructions, schedule, duration and marks.
3. Review exam details and candidate-facing view.
4. Publish the exam.
5. Enroll eligible candidates or use the existing authorized join process.
6. Monitor active attempts and issue announcements as required.
7. Review incidents with context.
8. Grade written responses and review objective totals.
9. Review results and explicitly publish.
10. Download authorized academic reports and inspect analytics.

### Candidate workflow

1. Sign in and view available/upcoming/completed exams.
2. Read instructions and access conditions.
3. Enter only during the authorized window.
4. Complete questions, navigate and mark for review.
5. See answer save/connectivity state and recover within the original time window.
6. Use the digital scratchpad and saved workspace preferences.
7. Review responses and submit, or be finalized by server expiry.
8. View own result only after publication.

### Administrator workflow

1. Sign in using existing secure account flow.
2. Manage users and roles.
3. Review operational/audit activity within platform permissions.
4. Never bypass exam ownership or tenant boundaries unless existing authorization explicitly allows it.

## 8. Success criteria

- All core requirements 3.1–3.8 have working, tested end-to-end flows.
- All eight secondary features 4.1–4.8 are functional and integrated, not static placeholders.
- At least challenge 5.3 is functional and demonstrable with an honest trust/limitation explanation.
- Legacy MCQ exams and attempts remain readable and usable after migrations.
- Existing authentication, proctoring, evidence, reporting and tenant isolation regressions are absent.
- Candidate answer writes are idempotent and time-validated server-side.
- Active attempt snapshots remain stable after source-question edits.
- No candidate can read another candidate's private data or an unpublished result.
- A 15-minute demo can show administrator, examiner, candidate, failure recovery, grading and publication.
- The app can be set up from the README using fictional/test data and no paid dependency.

## 9. Product design expectations

Use the existing UI framework and shared components. Build clear dashboards for each role, accessible form controls, responsive layouts, descriptive error states, consistent status labels and useful empty states. Avoid generic template styling and avoid redesigning stable pages without a direct requirement.

## 10. Official source

Requirements in this PRD are based on the user-provided *Web-e-Thon Problem Statement.pdf*, especially pages 1–7. The official brief requires all core features, all eight secondary features and at least one functional innovation challenge. It also states that non-functional placeholders do not receive full functional credit and prohibits commits, pushes, builds or deployments after the competition deadline.
