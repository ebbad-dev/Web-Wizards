# Phase 5 Prompt — Examination Monitoring and Announcements

Read the master prompt and all supporting docs, plus approved Phase 4 report. Execute **Phase 5 only**.

## Objective

Give examiners useful visibility into active exam progress and provide an authorized way to communicate exam-scoped announcements to candidates, reusing existing monitoring infrastructure.

## Scope

1. Build/extend an examiner active-attempt view with candidate/attempt status, progress counts, submitted/in-progress/expired state and last relevant activity.
2. Show existing monitoring incidents/events with timestamp and context; preserve evidence access restrictions.
3. Add examiner review/disposition notes only if the current data model supports safe audited review; do not turn a risk score into an automatic disciplinary decision.
4. Add exam-scoped announcements: create, list, edit/withdraw if appropriate; target only candidates assigned/eligible for the exam.
5. Display announcements to candidates on dashboard and/or active exam workspace using the project's existing query/polling or realtime pattern.
6. Add timestamps, author and read/visibility behavior only where useful; avoid overengineering receipts or complex notification delivery.
7. Audit announcement creation/update/withdrawal and protect all APIs by role, tenant and exam ownership.

## Compatibility constraints

- Reuse current proctoring event tables, risk logic and evidence store.
- Do not change signal scoring, event semantics or camera/audio/browser startup as part of this phase.
- Do not automatically fail attempts or deduct marks due to incidents.
- Keep candidate announcements free of private examiner notes and sensitive incident data.

## Acceptance gate

- Examiner sees live/recent progress for authorized exams only.
- Candidate sees announcements for the correct exam only.
- Unauthorized roles/tenants/candidates cannot read or create announcements.
- Monitoring context explicitly says signals require human review and are not conclusive proof.
- Existing event ingestion and evidence/report flows remain unchanged.
- Tests, regressions and phase report complete. Stop before Phase 6.
