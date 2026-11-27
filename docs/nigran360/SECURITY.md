# Security and Privacy Requirements — Nigran 360

## 1. Security objectives

Protect accounts, exam content, answer keys, candidate answers, PII, grades, results, proctoring events/evidence, reports, imports and tenant data. Enforce all authority at the backend. Preserve the existing security model and strengthen it without weakening current protections.

## 2. Threat model

Consider at minimum:

- candidate attempting to read another candidate's attempt/result;
- candidate changing exam/attempt/question IDs in API requests;
- candidate attempting writes after expiry or after submission;
- candidate attempting to inspect answer keys or private grading rubrics;
- examiner attempting to access another examiner's exam or tenant;
- unauthorized user invoking admin, grading, publishing, import or report endpoints;
- duplicate/replayed save or submit requests;
- malformed question/response payloads and SQL injection;
- malicious CSV/JSON uploads, oversized files, formula injection in exported CSV, path traversal and parser abuse;
- report ID enumeration, QR/token leakage or public endpoint PII exposure;
- sandbox data leaking into real reports/analytics;
- local browser storage exposing queued answers or scratchpad content on a shared device;
- false positives or over-interpretation of proctoring signals;
- secrets or personal data leaking into logs, CI artifacts or source control.

## 3. Authentication and authorization

- Reuse existing authentication/token/session design.
- Enforce roles and object-level checks in FastAPI/service layer.
- Scope every query by tenant and authorized owner/candidate.
- Re-check authorization for downloads, imports, sandbox access, grading and publication.
- Do not accept tenant IDs, role claims or ownership assertions from the client without server verification.
- Ensure disabled/revoked accounts/tokens follow current session invalidation policy.
- Protect admin bootstrap flows and never seed default production passwords.

## 4. Answer keys and candidate privacy

- Candidate APIs receive only attempt-specific question content and allowed choices.
- Never include `is_correct`, answer keys, private marking configuration or hidden examiner notes in candidate responses.
- Do not leak other candidate names, roll numbers, emails, responses or grades through list endpoints or analytics.
- Candidate result routes must bind the candidate identity from the authenticated principal, not a caller-supplied `user_id` alone.
- Scratchpad data is candidate/attempt-scoped and not examiner-visible by default.
- Local pending-answer storage is untrusted and potentially sensitive. Keep it minimal, bounded and cleared after confirmed completion/cleanup; never store access tokens with it.

## 5. Server-side time and data integrity

- Server UTC time defines start, deadline, accepted answer writes and finalization.
- New attempts store immutable deadline.
- Never rely on client wall-clock time for enforcement.
- Use transaction/locking strategy appropriate to SQL Server to prevent duplicate starts/submission races.
- Save retries must be idempotent.
- Submission and expiry must finalize once.
- Grade values must be constrained to allowed marks; totals are server-calculated.
- Results remain hidden until authorized publication.

## 6. SQL and API security

- Use parameterized SQL and existing repository abstractions.
- Validate IDs, enum values, string lengths, ranges and nested payloads with Pydantic and domain validation.
- Return safe error codes/messages; never return SQL exception details or stack traces to clients.
- Use request size and pagination limits.
- Protect CORS origins and require HTTPS in deployment.
- Apply rate limits or bounded abuse controls to login/reset, import, report verification and public endpoints if current infrastructure supports them.
- Keep security-sensitive operations auditable.

## 7. Import security

- Accept only documented CSV/JSON formats.
- Limit file size, row count, columns, nesting depth and string lengths.
- Reject malformed encodings and unsupported file types.
- Parse as data only; never execute formulas, scripts or code.
- Do not accept arbitrary file paths or write uploaded file names to the filesystem unchecked.
- Prevent CSV formula injection in any exported error/result CSV by escaping dangerous leading characters.
- Validate all rows before database transaction or clearly show partial import mode; default to all-or-nothing.
- Do not accept plaintext passwords or secret columns.

## 8. Reports and verification

- Authorize report creation and download by role, tenant and exam ownership.
- Use unguessable opaque verification tokens; do not use sequential report IDs as public verification credentials.
- Return minimal data from public verification: valid/invalid/revoked status, report type and issue date if approved. Do not return candidate PII, marks, answer details or evidence publicly.
- Consider token revocation/reissue and audit.
- Avoid embedding unnecessary PII in QR codes; QR should point to a verification URL with opaque token.

## 9. Sandbox isolation

- Sandbox attempts have a trusted server-created type/discriminator.
- Candidate cannot choose `is_sandbox=true` to bypass real workflows.
- All official metrics, attendance, grades, notifications, reports and exports exclude sandbox attempts.
- Add negative tests for every major aggregate and API view.

## 10. Proctoring and fairness

- Monitoring indicators are not conclusive proof of misconduct.
- Do not automatically fail, deduct marks or discipline candidates solely from risk scores or single browser signals.
- Preserve examiner review and audit context.
- Be transparent about camera/microphone/browser monitoring and existing platform limits.
- Do not overstate AI-site detection, extension enforcement or device trust; verify behavior in actual code and browsers.

## 11. Logging and secrets

- Never log passwords, auth tokens, report verification secrets, full private answer payloads, answer keys or unnecessary media/evidence.
- Keep `.env` and production secrets out of Git.
- Use existing secret configuration; do not hardcode secrets or test credentials.
- Ensure test fixtures use synthetic data and disposable credentials.
- Redact sensitive values from exception traces and audit metadata.

## 12. Security verification gates

For every phase, test unauthorized role, wrong tenant, wrong exam owner, wrong candidate, expired attempt, submitted attempt, duplicate request, invalid marks, unpublished result, sandbox leakage and malformed input as applicable. Phase 8 must perform a documented security review of all new routes and data-return paths.
