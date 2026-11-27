# Phase 7 Prompt — Remaining Secondary Features

Read the master prompt and all supporting docs, plus approved Phase 6 report. Execute **Phase 7 only**.

## Objective

Complete the remaining secondary features not already delivered in earlier phases: academic PDF reporting, isolated exam sandbox, bulk CSV/JSON import and verifiable reports.

## A. Academic PDF reports (official 4.2)

- Generate readable exam/candidate performance PDFs using actual submitted/graded data.
- Support authorized examiner reports and candidate's own permitted report where product policy allows.
- Keep these separate from existing proctoring PDF reports.
- Protect creation/download endpoints; enforce tenant, role and exam ownership.
- Avoid unnecessary personal data and never expose hidden answer keys.
- Include report identifier/verification token as designed in section D.

## B. Examination sandbox (official 4.3)

- Allow examiner to preview/experience the candidate exam workflow.
- Use a server-created sandbox discriminator or equivalent isolation.
- Sandbox must not affect real submissions, attendance, grades, publication, question analytics, PDF totals, exports or candidate dashboards.
- Prevent client users from converting their own real attempts into sandbox or vice versa.
- Clearly label sandbox UI; do not send real candidate notifications or trigger live disciplinary workflows.

## C. Bulk CSV/JSON import (official 4.4)

- Support documented CSV and JSON formats for candidate records and questions.
- Provide downloadable sample templates or schema documentation.
- Validate encoding, columns, rows, required values, duplicates, question types/options/keys, marks and category references.
- Provide preview/counts and row-specific actionable errors before write.
- Default to all-or-nothing database transaction when validation fails; if partial import is intentionally offered, make it explicit and safe.
- Bound file size, rows and field lengths. Prevent formula injection in any exported error CSV.
- Never accept passwords in uploaded candidate records or store raw uploads indefinitely without a retention reason.
- Record import audit metadata.

## D. Verifiable reports (official 4.6)

- Generate secure opaque verification identifiers or signed tokens.
- QR contains a verification URL/token only, not candidate PII or marks.
- Verification endpoint returns minimal authenticity fields (valid/invalid/revoked, report type and issue date if approved).
- Avoid sequential guessable IDs and brute-force-friendly behavior.
- Support revoke/reissue with audit.
- Verify token privacy and enumeration resistance.

## Cross-check earlier secondary features

Re-run acceptance tests for:
- 4.1 Network-aware state and sync behavior (Phase 4).
- 4.5 Question analytics (Phase 6).
- 4.7 Workspace preferences (Phase 3).
- 4.8 Digital scratchpad (Phase 3).

## Acceptance gate

- Academic PDFs are based on actual performance data and access restricted.
- Sandbox does not contaminate any real view/report/aggregate.
- CSV/JSON import provides preview and useful validation errors, uses safe transaction behavior and is authorization-protected.
- Report QR/token verifies authenticity without unnecessary personal data exposure.
- All eight secondary features are demonstrably functional.
- Existing proctoring PDF/report and operations flows remain unchanged. Complete report and stop before Phase 8.
