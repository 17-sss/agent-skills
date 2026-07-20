# Reviewed Plan Review Contracts

Use these contracts for every Reviewed Plan review cycle. Roles are review responsibilities, not hidden runtime identities.

## Shared input

Provide each role with:

- the exact user request, constraints, and non-goals
- applicable repository instructions
- concrete file, symbol, and test evidence
- the current plan revision
- prior verdicts that the role must evaluate or verify
- proof of a tool-enforced Codex `read-only` sandbox, not only a prose contract

Do not ask a role to edit files, run formatters or generators, install dependencies, or begin implementation.

## Planner

Produce:

- a right-sized ordered implementation sequence
- relevant files and symbols for every material step
- decision drivers and viable alternatives
- testable acceptance criteria
- risk, rollback, and verification strategy
- explicit assumptions and unresolved decisions

Do not force a fixed number of steps. For one viable approach, explain why the alternatives fail the task constraints.

## Architect

Review:

- ownership and system boundaries
- coupling and reuse of existing abstractions
- compatibility and public contracts
- data, migration, security, and operational consequences
- rollout and rollback safety
- the strongest credible alternative and its tradeoff

Return exactly one verdict:

- `ACCEPT` — structurally sound enough for Critic review
- `REVISE` — name the defects and required plan changes

Architect acceptance is not final approval.

## Critic

Run only after Architect acceptance. Review:

- requirement and non-goal coverage
- plan executability and ordering
- regression and edge-case coverage
- acceptance-criteria testability
- specificity of verification commands and observations
- risk mitigation and rollback sufficiency
- consistency between decisions, alternatives, and consequences

Return exactly one verdict:

- `APPROVE` — the current revision is implementation-ready
- `ITERATE` — concrete revisions can make it ready
- `REJECT` — a missing decision, evidence gap, or unacceptable risk prevents approval

Attach every non-approval finding to a required revision or user decision.

## Workspace integrity

Native subagents inherit the parent permission mode. Before either independent gate, confirm that the child effective sandbox is read-only or use a separate native Codex execution explicitly configured read-only. If this cannot be enforced, the gate is unavailable and the plan is `NOT APPROVED`. Do not treat a custom-agent default as sufficient when a live parent permission override can supersede it.

Before each delegated review, capture a deterministic content fingerprint over:

- the current `HEAD` identifier
- exact staged and unstaged diff bytes, including binary changes
- a canonical serialization of each untracked path's normalized relative path, file type, executable mode bits, symlink target when applicable, and complete content or content hash

Capture `git status --short` as human-readable context, but do not use status text as the mutation detector: editing an already-modified or already-untracked file may leave it unchanged. Recompute the content fingerprint after each delegated review and before the final response. If it differs, stop the review sequence with `NOT APPROVED`, report the changed paths, discard the affected verdict, and preserve the user's worktree without reverting it.
