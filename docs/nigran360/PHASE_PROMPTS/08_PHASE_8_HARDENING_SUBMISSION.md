# Phase 8 Prompt — Integrated Hardening and Submission Readiness

Read the master prompt and all supporting docs, plus approved reports for Phases 0–7. Execute **Phase 8 only**. This is an integration and verification phase, not an invitation to add unrelated features.

## Objective

Prove Nigran 360 works end-to-end, protects existing behavior and meets the competition brief. Fix only verified defects that are in scope and can be safely corrected before the applicable deadline.

## Required verification

1. Run the full current Python/regression/security suite.
2. Run frontend typecheck and production build.
3. Run migration tests against an existing-data fixture and SQL Server.
4. Run SQL Server live smoke tests for attempt concurrency/idempotency, deadline and grading persistence when available.
5. Run complete administrator, examiner and candidate E2E flows.
6. Verify all core requirements 3.1–3.8.
7. Verify every secondary feature 4.1–4.8.
8. Demonstrate innovation 5.3 with network interruption, safe queue/reconnect, persisted answers and unchanged server deadline.
9. Test unauthorized roles, wrong tenant, wrong exam owner/candidate, unpublished results, report access and sandbox leakage.
10. Test refresh, double-click, duplicate request, interrupted request, simultaneous requests, stale response and expiry edge cases.
11. Verify accessibility basics: keyboard navigation, focus indicators, labels, contrast, status announcements and responsive layouts.
12. Verify PDF readability, QR/report verification privacy and import safety.
13. Verify README setup instructions and environment assumptions against actual scripts.
14. Prepare fictional demo accounts/data and a 15-minute live demo flow. Never place real secrets in README or Git.
15. Review logs for accidental secrets, PII, answer keys or scratchpad content.
16. Confirm backups and recovery procedure for the SQL Server database.

## Documentation outputs

- Update root README with Nigran 360 branding and accurate setup/workflow instructions without removing useful ProctorAI operational detail.
- Add roles/test credentials instructions using local-only or disposable test-account provisioning; do not commit secrets.
- Add innovation 5.3 explanation with trust assumptions and limitations.
- Add system architecture/data flow summary.
- Add migration/backup notes and troubleshooting.
- Add a traceability table mapping official requirements to routes/screens/tests.
- Prepare a concise 15-minute demo script.

## Competition cutoff safety

The official brief prohibits commits, pushes, builds and deployments after the competition deadline. Verify the exact cutoff from the official competition guide or user. Do not infer it. Before cutoff, any deployment/build requires explicit user authorization and a rollback plan. At/after cutoff, do not commit, push, build or deploy. Do not manipulate timestamps or attempt a workaround. You may document the state and report blockers without violating the rule.

## Final acceptance gate

- All implemented features are functional and integrated, not placeholder controls.
- All known required checks pass, or any blocker is explicitly listed as `NOT RUN`/`BLOCKED`.
- No known critical/high security or data-integrity defect remains.
- Legacy MCQ and existing proctoring behavior are protected by regression results.
- All requirement mappings are supported by evidence.
- Demo data and role setup are safe and reproducible.
- The final report contains exact commands/results, risks, limitations and cutoff status.
- Stop after the final report; do not make unrequested pushes/deployments.
