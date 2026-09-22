# Skill maintenance handoff — 2026-09-22

Baseline: `main` at `bd61e53`; the worktree was clean before this work. All counts below use whitespace-separated **words**, not tokens, from `HEAD` and the local working tree. Package names, invocation policy, runtime grouping, and standalone installation remain unchanged. This is a local-only handoff; no commit, push, PR, deployment, installed-skill sync, HANDOFF, or project-chronicle update was made.

## Contract map and entrypoint size

The entrypoint keeps each skill's trigger, required route, stop conditions, and authority boundary. Conditional detail is linked directly from the route that needs it.

| Skill | `SKILL.md` before → after | Decision and preserved contract location |
| --- | ---: | --- |
| `audio-asset-generator` | 1,565 → 1,347 | Keep provider/cost/rights/listening gates in entrypoint; category prompts in `references/prompt-specifications.md`, browser delivery behind its existing conditional link. |
| `commit-helper` | 581 → 575 | Remove one duplicate commit example; keep one draft/commit path, staged-only scope, style rules, and script behavior. |
| `completion-loop` | 1,754 → 1,575 | Keep scope, evidence invalidation, risk gate, and final judgment in entrypoint/`verification-contract.md`; independent packet, isolation, and review budget in conditional `independent-review.md`. |
| `design-loop` | 1,362 → 1,250 | Keep implementation/render/interaction loop, baseline viewport and capture discipline, and visual gate; audit, alternatives, rule extraction, and optional capability routing in `surface-capability-guide.md`. |
| `github-pr-publish` | 1,222 → 1,041 | Keep preview, explicit execution, remote/head checks, and standard example; SSH and REST exceptions in existing references. Package-local redaction helper serves both scripts. |
| `github-pr-review` | 1,718 → 1,475 | Keep evidence/diff scope, posting authorization, and head check; manual collection in `collection-fallback.md`, posting detail in `posting-reviews.md`. Remove raw-token request exception. Package-local redaction helper serves both scripts. |
| `godot-dev-loop` | 1,076 → 897 | Keep INBOX → DESIGN → STATUS, real-window capture, STOP/BLOCKED; first-use setup in `bootstrap-contract.md`, existing-project runner detail in `fresh-runner-contract.md`. |
| `handoff-memory` | 1,225 → 1,094 | Keep selection, ambiguity stop, stale check, snapshot and companion boundaries, including prior authorization when both workflows were requested; detailed start/close-out route is conditional in `agent-usage-best-practices.md`. |
| `milestone-runner` | 1,095 → 1,095 | Retain: entrypoint is the ordered state/goal procedure; `state-contract.md` owns schema and recovery detail. No safe duplicate removal outweighed the risk of weakening revision/final-gate wording. |
| `minimal` | 713 → 713 | Retain: explicit-only, bounded simplification already states that it cannot override the active workflow's approval, validation, or test gates. |
| `project-chronicle` | 1,303 → 1,209 | Keep Bootstrap/Record/Read choice, evidence and log rules; document layers in `document-model.md` and recording detail in existing references. |
| `review-gate` | 1,678 → 1,678 | Retain: two-lane read-only review, snapshot identity, sensitive packet isolation, and verdict rules have no safe optional split in this pass. |
| `reviewed-plan` | 1,146 → 1,008 | Keep Planner → Architect → Critic order, same-revision acceptance, bounded retries, and no implementation; role inputs/outputs in `review-contracts.md`, optional next step condensed. |
| `spec-interview` | 1,220 → 987 | Keep one decision per round, readiness and no implementation; optional read-only delegation in `delegated-inspection.md`, optional next step condensed. |
| `visual-match` | 1,676 → 1,596 | Keep equivalent capture conditions, fixed scoring, pre-edit gate, and final image audit; live URL/generated-image/no-renderer/scorer detail routed to `capability-routing.md`. |

The checker still compares its installable inventory, independent package set, Codex-dependent set, marketplace grouping, and package links. Optional handoff checks use short section-scoped patterns instead of exact full sentences; tests still reject missing guards and mandatory or out-of-section sibling calls. New conditional links are covered by package link validation.

## Representative required reading

Counts include the entrypoint and references required for the named route. A conditional reference is counted only when that route uses it. These are word counts, not model token estimates.

| Route and required references | Before → after |
| --- | ---: |
| Spec interview, direct inspection: entrypoint | 1,220 → 987 |
| Reviewed plan: entrypoint + `review-contracts.md` | 1,689 → 1,551 |
| Completion Loop Low-risk: entrypoint + `verification-contract.md` | 3,782 → 3,306 |
| Completion Loop with independent review: previous two + new `independent-review.md` only after change | 3,782 → 3,676 |
| Design Loop ordinary build: entrypoint + `visual-review-rubric.md` | 1,983 → 1,871 |
| Visual Match approved static image with an already selected capture tool: entrypoint + verdict + rubric, plus formerly mandatory capability routing before change | 4,668 → 3,627 |
| Audio procedural SFX: entrypoint + `provider-routing.md` | 2,318 → 2,100 |
| Godot existing project: entrypoint + project state + visual QA + fresh runner | 2,434 → 2,367 |
| PR publish standard route: entrypoint | 1,222 → 1,041 |
| PR review read-only route: entrypoint | 1,718 → 1,475 |

The PR redaction fix adds executable script code and tests; its safety cost is separate from the entrypoint reading reductions.

A follow-up contract audit restored ordinary Design Loop viewport/capture discipline and Visual Match capture equivalence in their entrypoints, and preserved an already authorized Handoff Memory plus Chronicle request. It also extended both PR redaction helpers to cover quoted authorization values. The table and route counts above include those corrections.

## Verification and limits

The baseline had 136 unit tests, 15 validator passes, 22 commit-helper evaluations, 26 publish tests, and 5 review tests. The original review collector's `Authorization: Bearer` substitution left the fake secret value in the output; that failure was reproduced against `HEAD` before the fix.

After this work: 137 unit tests, 15 installable-package validator passes, 22 commit-helper evaluations, 29 publish tests, 8 review tests, and `git diff --check` passed. PR fixtures cover Bearer/Basic/token case, spacing, and quoted values; token prefixes, environment assignments, credentialed URLs, JSON parsing, command failure status, private output permissions, sanitizer failure, preview, remote/head rejection, and interrupt cleanup. A local procedural `ui-click` run produced a readable 7,982-byte mono PCM WAV at 44,100 Hz.

An existing Firefox executable was tried against a disposable local HTML capture fixture, but its screenshot command timed out after 25 seconds; no screenshot was verified. No Godot executable was available. No listening or real game-window capture occurred. No live GitHub write or real credential was used. No blind model-level before/after workflow evaluation was run, so static contract and fixture results do not establish cross-agent behavioral equivalence. Those paths remain unverified, not passed.
