# Managed workflow forward-test report

This file records behavioral evidence that cannot be established by schema validation alone. Tests run only in disposable Git repositories under `/tmp`; no dependency installation, external write, user-configuration change, or production access is allowed.

## 2026-07-23 anchored scoring contract update

Status: pending forward test. The package-local scorer now calculates a fixed-weight `visual_similarity_percent`, uses the lowest equivalent target score, and refuses a visual pass candidate below the accepted threshold, with low confidence, or while blocking or major differences remain. Unit and structural validation can prove the arithmetic and standalone dependency boundary, but the browser-enabled trace must still demonstrate honest component classification from rendered evidence. Optional pixel similarity must remain separate and nullable.

## 2026-07-21 renderer-bootstrap contract update

Status: pending forward test. `visual-match` now offers an explicit, repository-isolated Chromium bootstrap before returning `BLOCKED` when no renderer exists. The 2026-07-20 safety-blocker trace predates that approval step and does not prove the revised contract. Re-run the missing-renderer path with installation prohibited and verify that it proposes the bounded bootstrap without downloading anything or changing the fixture. The browser-enabled success path also remains pending.

## 2026-07-20 review

Status: partial. Five workflow success paths and the Visual Match safety-blocker path are complete; the browser-enabled Visual Match success path remains pending. Update this table only from fresh traces and before/after fingerprints.

| Skill | Scenario | Result | Evidence |
| --- | --- | --- | --- |
| `spec-interview` | Ambiguous organization-level API-key ownership in an existing user-owned key model | PASS | Inspected repository contract, asked one ownership decision, made no fixture change |
| `reviewed-plan` | Backward-compatible migration from process-local to server-managed sessions | PASS | Planner revised through four sequential Architect gates, then received Architect `ACCEPT` and Critic `APPROVE`; fixture remained clean at baseline `c31e0d6` |
| `completion-loop` | Fix username canonicalization with existing regression tests | PASS | Reproduced both failures, changed one implementation line, passed 2/2 tests and `git diff --check`, received a clean independent review, and preserved the reviewed fingerprint; forward run used 21,323 tokens over 5m 12s |
| `milestone-runner` | Two-stage durable migration with sequential checkpoints, test-first implementation, final review, and native goal reconciliation | PASS | Completed G001 then G002 in an isolated fixture; 4 unittests and a 29-assertion matrix passed, the 6-event ledger validated, an independent read-only review found no issue, and no sibling skill was invoked or inspected |
| `visual-match` | Missing-browser safety path for an approved static reference | BLOCKED (environment, expected) | Preflight found `playwright-cli` but no installed Chromium, Chrome, Firefox, WebKit, or Edge; returned `BLOCKED` before editing, left Git clean, and made no parity claim |
| `visual-match` | Browser-enabled baseline, seeded mismatch, repair, equivalent recapture, interaction check, and residual-difference report | PENDING | No browser was installed because the test boundary prohibited dependency or environment changes; the full render-success loop remains unproven |
| `review-gate` | Review staged authorization, unstaged cache isolation, and untracked path-handling changes; separately audit one explicit file without a baseline | PASS | Change mode used snapshot `37d755c…` and found all three seeded P1 blockers; file-audit mode used the complete 82-byte file snapshot `50cea874…` without inventing change attribution; both runs returned `REQUEST_CHANGES` and preserved exact bytes/status |

## Release rule

Treat any `PENDING`, stale contract evidence, `FAIL`, unexpected workspace write, missing independent gate, evidence-free success, or undocumented capability gap as not release-ready. The five non-visual skills are eligible for release from this matrix; the current `visual-match` contract is not release-ready until both the revised missing-renderer approval path and the browser-enabled row pass. Delete disposable fixtures and task-scoped captures after the evidence has been summarized here.
