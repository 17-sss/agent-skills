# Codex-native workflow forward-test report

This file records behavioral evidence that cannot be established by schema validation alone. Tests run only in disposable Git repositories under `/tmp`; no dependency installation, external write, user-configuration change, or production access is allowed.

## 2026-07-20 review

Status: partial. Four workflow success paths and the Visual Match safety-blocker path are complete; the browser-enabled Visual Match success path remains pending. Update this table only from fresh traces and before/after fingerprints.

| Skill | Scenario | Result | Evidence |
| --- | --- | --- | --- |
| `spec-interview` | Ambiguous organization-level API-key ownership in an existing user-owned key model | PASS | Inspected repository contract, asked one ownership decision, made no fixture change |
| `reviewed-plan` | Backward-compatible migration from process-local to server-managed sessions | PASS | Planner revised through four sequential Architect gates, then received Architect `ACCEPT` and Critic `APPROVE`; fixture remained clean at baseline `c31e0d6` |
| `completion-loop` | Fix username canonicalization with existing regression tests | PASS | Reproduced both failures, changed one implementation line, passed 2/2 tests and `git diff --check`, received a clean independent review, and preserved the reviewed fingerprint; forward run used 21,323 tokens over 5m 12s |
| `visual-match` | Missing-browser safety path for an approved static reference | BLOCKED (environment, expected) | Preflight found `playwright-cli` but no installed Chromium, Chrome, Firefox, WebKit, or Edge; returned `BLOCKED` before editing, left Git clean, and made no parity claim |
| `visual-match` | Browser-enabled baseline, seeded mismatch, repair, equivalent recapture, interaction check, and residual-difference report | PENDING | No browser was installed because the test boundary prohibited dependency or environment changes; the full render-success loop remains unproven |
| `review-gate` | Review staged authorization, unstaged cache isolation, and untracked path-handling changes; separately audit one explicit file without a baseline | PASS | Change mode used snapshot `37d755c…` and found all three seeded P1 blockers; file-audit mode used the complete 82-byte file snapshot `50cea874…` without inventing change attribution; both runs returned `REQUEST_CHANGES` and preserved exact bytes/status |

## Release rule

Treat any `PENDING`, `FAIL`, unexpected workspace write, missing independent gate, evidence-free success, or undocumented capability gap as not release-ready. The four non-visual skills are eligible for release from this matrix; `visual-match` remains conditionally ready only for its safe blocker behavior until the browser-enabled row passes. Delete disposable fixtures and task-scoped captures after the evidence has been summarized here.
