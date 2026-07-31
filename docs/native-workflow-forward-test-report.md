# Managed workflow forward-test report

This file records behavioral evidence that cannot be established by schema validation alone. Tests run only in disposable Git repositories under `/tmp`; no dependency installation, external write, user-configuration change, or production access is allowed.

## 2026-07-31 Visual Match A/B and browser-enabled forward test

Status: PASS for the browser-enabled visual repair path. An approved three-view reference set and an older runnable implementation from the same design family were captured with the same existing system Firefox harness. The target implementation source was withheld from every implementation and judging lane. No dependency, browser, plugin, runtime state, repository artifact, or user configuration was installed or changed by the test.

The current upstream visual workflow and the pre-change `visual-match` each received the same baseline, reference PNGs, viewport/state contract, and four-repair budget. The upstream lane produced a semantic pass at 96 and pixel similarities of 99.140%, 95.807%, and 96.199%. The pre-change lane produced a self-reported semantic pass at 99, but a source-blind judge scored it 92.8 because its desktop result flattened repeated card containers; the upstream result scored 98.0 in that comparison. This demonstrated why semantic grouping cannot be inferred from aggregate pixel similarity or a non-independent score.

The revised `visual-match` adds outside-in landmark diagnosis, explicit repeated-container grouping, coherent multi-ID repair batches, a Python-standard-library PNG hotspot helper, and a fresh raw-pair audit after the first pass candidate. A new run from the untouched baseline converged in three repair batches:

| Iteration | Semantic score | Home pixel | Community desktop pixel | Community mobile pixel |
| ---: | ---: | ---: | ---: | ---: |
| Baseline | 80 | 98.920% | 89.748% | 83.825% |
| After batch 1 | 93 | 99.140% | 93.018% | 91.164% |
| After batch 2 | 94 | 99.140% | 96.486% | 91.761% |
| After batch 3 | 99 | 99.140% | 96.450% | 91.965% |

The first pass was frozen and independently audited from only the six raw PNGs and capture contract. That audit returned zero blocking, major, or minor findings. A post-audit recapture was byte-identical. A final fresh image-only judge then scored the revised result 97.4 versus 92.8 for the upstream lane, preferring the revised repeated-card boundaries, bookmarks, title-width reservation, and solved-title grouping. The implementation lane accidentally saw a sibling result summary only after the implementation and audited captures were already frozen; no later UI edit occurred, and the final image-only judge was isolated from that exposure.

The browser success path therefore passes. The separate no-renderer approval/decline path remains pending because this trace reused an already installed system renderer and intentionally performed no bootstrap.

## 2026-07-31 Completion Loop scope-control forward test

Status: PASS. A disposable local-only Python fixture froze username normalization and Unicode preservation as acceptance criteria, explicitly excluded deployment infrastructure, and supplied two incoming review observations without their expected classifications. The revised `completion-loop` fixed the reproducible Unicode-loss regression, passed both targeted tests and `git diff --check`, classified missing Kubernetes readiness as deferred, and finished with zero blockers. It changed one implementation line and created no dependency, deployment artifact, commit, push, PR, or external write.

Static contract tests additionally pin local-only Kubernetes deferral, out-of-scope findings during focused rereview, evidence-ledger deduplication, material-expansion checkpoints, current-fix regressions remaining blockers, and a single final full-verification budget.

## 2026-07-23 marketplace security hardening

Status: pending external rescan and forward test. `design-loop` no longer ships a redundant self-install URL inside its package. `review-gate` now keeps the original target fingerprint in the parent context, removes credential values from delegated review packets, requires packet-only lane visibility when sensitive material exists, and returns `INCONCLUSIVE` when redaction removes material evidence. Structural tests can prove these package contracts; a fresh disposable trace must still demonstrate that seeded credentials never reach either lane, and the public registry labels cannot update until the committed revision is published and rescanned.

## 2026-07-23 choice-first interview contract update

Status: pending forward test. `spec-interview` now prefers native structured-choice input for bounded decisions, preserves one decision per round and a custom-answer escape hatch, and falls back to an equivalent numbered list when structured input is unavailable. Structural tests can prove the contract text, but a fresh trace must still show that the agent uses choices only for complete option sets and keeps genuinely open-ended questions free-form.

## 2026-07-23 anchored scoring contract update

Status: PASS for the browser-enabled path. The 2026-07-31 trace demonstrated fixed-weight `visual_similarity_percent`, lowest-target aggregation, blocking/major pass prevention, stable difference IDs, a fresh pass audit, and separate nullable pixel evidence against real rendered PNG pairs. The no-renderer path remains independently pending.

## 2026-07-21 renderer-bootstrap contract update

Status: partial. The 2026-07-31 browser-enabled success path passed with an existing system renderer and no installation. The 2026-07-20 safety-blocker trace predates the approval step and does not prove the revised no-renderer contract. Re-run that path with installation prohibited and verify that it proposes the bounded bootstrap without downloading anything or changing the fixture.

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

Treat any `PENDING`, stale contract evidence, `FAIL`, unexpected workspace write, missing independent gate, evidence-free success, or undocumented capability gap as not release-ready. `reviewed-plan`, `completion-loop`, and `milestone-runner` are eligible for release from this matrix. The revised `spec-interview` choice-presentation and `review-gate` sensitive-packet contracts need fresh traces. The `visual-match` browser-enabled repair path is release-ready from the 2026-07-31 evidence, while its no-renderer bootstrap path remains pending. Delete disposable fixtures and task-scoped captures after the evidence has been summarized here.
