---
name: reviewed-plan
description: Create a read-only, evidence-grounded implementation plan and validate it through sequential Planner, Architect, and Critic review. Use when the user invokes $reviewed-plan, requests consensus planning, needs architecture-heavy or high-risk work reviewed before implementation, or wants an approved implementation handoff with concrete verification criteria.
---

# Reviewed Plan

Recommended invocation: `/plan $reviewed-plan <task>`.

Remain in planning mode. Inspect the workspace and external references, but do not modify project files, run generators or formatters, install packages, or begin implementation. Capture the initial workspace content fingerprint described in the review contract and compare it after each delegated gate and before the final response; never revert unexpected user changes.

Read [review-contracts.md](references/review-contracts.md) before starting the role passes.

## Ground the plan

1. Inspect applicable instructions, documentation, relevant files, symbols, tests, configuration, and recent repository patterns.
2. Separate observed facts from inferences and unresolved user decisions.
3. Ask one focused question only when the answer would materially change architecture, scope, safety, or acceptance criteria.
4. Research authoritative external sources when the plan depends on version-sensitive APIs, standards, or dependency behavior.
5. Identify the repository commands that should later prove correctness, but do not run commands that may create or modify project artifacts during this planning workflow.

## Run the review sequence

The main context may own the Planner draft. Require fresh native Codex reviewers for the Architect and Critic gates. Do not simulate either independent gate in the authoring context.

Preflight tool-enforced reviewer isolation before launching the sequence. Native subagents inherit the parent permission mode, so a read-only prompt is insufficient. Use subagents only when the parent turn's effective sandbox is read-only, or use another native isolated Codex run whose effective sandbox is explicitly `read-only`. Keep connector and app tools non-mutating as well. Each Architect or Critic is a terminal review lane: do not let it activate another workflow or delegate recursively. If neither route is available, stop with `NOT APPROVED` and name the missing isolation gate. Content fingerprints remain defense in depth, not the safety boundary.

If an Architect or Critic reviewer is unavailable, fails, or returns no evidence, stop with the best provisional plan marked `NOT APPROVED`, name the missing gate, and do not report consensus.

If the workspace fingerprint changes during a delegated gate, stop with `NOT APPROVED`, report the exact changed paths, preserve the files, and do not reuse that gate's verdict.

1. **Planner** — create the initial implementation plan, acceptance criteria, viable alternatives, risks, and verification strategy from repository evidence.
2. **Architect** — review the draft for boundaries, compatibility, coupling, migration safety, operational risk, and the strongest credible alternative. Wait for this pass to finish.
3. If Architect returns `REVISE`, revise the plan and obtain a new Architect verdict before continuing.
4. **Critic** — run only after Architect returns `ACCEPT`. Check completeness, executability, regression risk, testability, rollback coverage, and evidence quality.
5. If Critic returns `ITERATE` or `REJECT`, revise through Planner, then repeat Architect before Critic.

Never run Architect and Critic in parallel. Never treat planning artifacts or a Planner draft as consensus evidence.

Limit the full review sequence to five cycles. If approval is still unavailable, return the best current plan with `NOT APPROVED`, the unresolved findings, and the decision or evidence needed to proceed.

For security, authentication, data migration, destructive operations, public contract changes, compliance, or production risk, also require:

- explicit decision drivers and at least two viable options, or a reason alternatives are invalid
- concrete failure scenarios
- rollback or containment strategy
- unit, integration, end-to-end, and operational verification where applicable

## Produce the handoff

The final plan must include:

- requirements summary and non-goals
- testable acceptance criteria
- relevant files and symbols
- ordered implementation steps
- decisions, drivers, alternatives, and consequences
- risks and mitigations
- test, typecheck, lint, build, runtime, and review methods as applicable
- Architect and Critic verdicts
- unresolved issues and assumptions
- a clear implementation handoff with its stop condition

Report consensus only when Architect returned `ACCEPT` and the subsequent Critic returned `APPROVE` for the same plan revision. Stop after the handoff; implementation belongs to a new execution workflow.

## Offer an optional next workflow

Keep this package complete on its own. Do not invoke or activate another skill. Treat a downstream skill as available only when the current Codex task's available-skill inventory explicitly advertises its exact name. Do not inspect the filesystem, installation directories, catalog files, or downstream skill contents to infer availability. Do not install a missing skill. If the inventory is unavailable, treat every downstream skill as unavailable. Do not mention unavailable skills. Availability is not authorization: the user explicitly chooses and invokes any suggested workflow in a later turn.

Offer at most one recommendation and one genuinely applicable alternative only when Architect returned `ACCEPT` and the subsequent Critic returned `APPROVE` for the same plan revision, the handoff is executable, and no material user decision remains. Omit this section when the handoff is `NOT APPROVED`, either review gate is missing, a material decision remains unresolved, or the user asks to stop without follow-up suggestions.

Choose the best-fit route first, then check whether that exact skill is available:

- Suggest `$milestone-runner` when the approved plan has multiple ordered, independently verifiable, restartable stages.
- Suggest `$completion-loop` when the approved plan targets one coherent implementation outcome with concrete acceptance and verification criteria.

Do not substitute a weaker route merely because the best-fit skill is unavailable. If durable milestones are necessary and `$milestone-runner` is unavailable, suggest `$completion-loop` only when the approved plan can still be executed safely as one goal.

Render the recommendation as a copyable invocation under `Optional next workflow`. Stop after the suggestion; do not begin implementation.
