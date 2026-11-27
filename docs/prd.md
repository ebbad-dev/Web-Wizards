# NIGRAN-360 — Product Requirements Document

## Business Objective

Enable institutions and competition organizers to create, conduct, monitor and evaluate online examinations with academic integrity, fairness, network resilience and transparent dispute resolution.

## User Roles

| Role | Key Capabilities |
|---|---|
| Administrator | Manage users, roles, platform operations |
| Examiner | Create exams, manage questions and candidates, monitor, grade, publish |
| Candidate | Access exams, submit answers, view results, dispute |

## Core Workflows

1. Examiner creates exam → adds questions from bank → enrolls candidates → publishes
2. Candidate logs in → sees available exam → starts attempt (server records deadline)
3. Candidate answers questions, answers autosave, timer counts down from server deadline
4. Exam auto-submits at deadline or candidate submits early
5. Auto-grading runs for MCQ; examiner manually grades written responses
6. Examiner reviews results → publishes → candidate views result
7. Candidate submits dispute → examiner reviews evidence → resolves with note → audit recorded

## Innovation Challenge: 5.4 Trust & Dispute Resolution

A transparent, auditable dispute workflow:
- Candidates submit disputes with category (grading error, ambiguous question, technical incident)
- Examiners review original answers, auto/manual scores, and add investigation notes
- Decision (resolved/rejected) with mandatory reason is recorded with actor and timestamp
- Full audit history is immutable and accessible to authorized parties
- Original scores are preserved alongside revised scores

## Acceptance Criteria Summary

- All three roles authenticate and see role-appropriate dashboards
- Candidates cannot access unpublished or non-enrolled exams
- Attempt deadline is server-authoritative; refresh preserves remaining time
- Answers are saved to DB and confirmed before "saved" is shown to candidate
- Auto-grading produces correct scores for MCQ and multi-select
- Results are not visible to candidates until published
- Disputes can be submitted, reviewed, resolved, and audited end-to-end
- PDFs can be downloaded by authorized users and verified by QR code
