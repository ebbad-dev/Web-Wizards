# Nigran 360 — Web-e-Thon Engineering Handoff

This package is the product, engineering, security, testing and phased implementation brief for evolving the existing **ProctorAI** application into **Nigran 360** for the Technoverse 5.0 Web-e-Thon Secure Examination Management System challenge.

> **Important:** These documents are implementation instructions, not proof that a requirement is already implemented. The coding agent must inspect the current repository and verify every baseline statement before changing code.

## Start here

1. Give the coding agent the entire `docs/nigran360/` folder as context.
2. Open and provide `MASTER_PROMPT.md` as the first prompt.
3. Run **Phase 0 only** using `PHASE_PROMPTS/00_PHASE_0_BASELINE_AND_COMPATIBILITY.md`.
4. Review the Phase 0 report and approve the resulting plan before asking the agent to execute Phase 1.
5. Execute one phase at a time. Use the corresponding prompt file and stop at each phase gate.

Do not ask the agent to implement all phases in one unreviewed pass. The phase gates are deliberately part of the safety strategy.

## Package contents

| File | Purpose |
|---|---|
| `MASTER_PROMPT.md` | Main prompt for Claude Code or another repository-aware coding agent |
| `PROJECT_BASELINE.md` | Verified starting-point snapshot and existing capabilities to protect |
| `PRD.md` | Product goals, users, scope and feature roadmap |
| `SRS.md` | Testable functional and non-functional requirements |
| `ARCHITECTURE.md` | Target architecture and integration guidance |
| `DATA_AND_MIGRATIONS.md` | Data model principles, snapshots, SQL Server migration safety |
| `SECURITY.md` | Security and privacy requirements |
| `TESTING.md` | Test strategy, phase gates and regression expectations |
| `IMPLEMENTATION.md` | Dependency-ordered execution plan and traceability |
| `PHASE_PROMPTS/` | Focused, copy-ready prompts for Phases 0–8 |
| `TEMPLATES/PHASE_COMPLETION_REPORT.md` | Required report format after every phase |
| `TEMPLATES/DECISION_LOG.md` | Architecture and product decision record template |

## Project and repository

- Product name: **Nigran 360**.
- Existing repository: <https://github.com/ebbad-dev/Proctor-Ai>
- Repository default branch: `main`.
- Baseline head verified while preparing this handoff: `8eb5c9fe4229faf8e5d11facba934dc9d8058a1d`.
- Existing stack: React + TypeScript frontend, TanStack Router/Start and Query, Tailwind/Radix UI; FastAPI + Pydantic + Uvicorn backend; Microsoft SQL Server using `pyodbc`; existing proctoring sidecar and ReportLab PDF utilities.

The product name may be updated in user-facing branding, but do not perform a broad destructive rename of package names, database names, environment variables, routes, identifiers or persisted data. Keep compatibility unless a reviewed migration plan explicitly justifies a change.

## Official brief

The governing source is the user-provided **Web-e-Thon Problem Statement.pdf**, 7 pages, titled *Secure Examination Management System*. It requires all listed core functionality, all eight secondary features, and at least one functional innovation challenge. Evaluation weights are 30 core, 15 secondary, 20 technical quality/reliability, 15 innovation and 20 UI/UX. See `PRD.md` and `SRS.md` for the detailed mapping.

The selected innovation focus for this plan is **5.3 Failure-Resilient Examinations**. The implementation must reduce the impact of ordinary connection/device interruption without pausing the authoritative timer or giving candidates an unverified extra-time advantage. Do not claim that a browser can cryptographically prove when unsynced offline answers were written; it cannot be safely trusted to do so.

## Critical competition cutoff rule

The official brief says no commits, pushes, builds or deployments may be made after the competition deadline, and timestamp manipulation is prohibited. The agent must obtain the actual deadline from the official competition guide or the user; do not infer it. Before that cutoff, complete the permitted build/deployment and save evidence. At or after the cutoff, stop all prohibited operations. Never bypass or manipulate the deadline.
