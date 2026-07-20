---
name: review-gate
description: Review a Git change set or explicit files without modifying them by combining independent Codex-native correctness and architecture lanes, then return prioritized file-and-line findings and a deterministic readiness verdict. Use when the user invokes $review-gate, requests a comprehensive code review, wants current changes, files, or a commit reviewed, or asks for an evidence-grounded quality, security, regression, test-gap, performance, or maintainability assessment.
---

# Review Gate

Recommended invocation: `Use $review-gate to review <files, commit, branch, checked-out PR-style target, or current changes>.`

Use native `/review` for a standard single-reviewer pass or its interactive Git target picker. Use this skill when the user wants the stronger two-lane review and deterministic merge gate below. If the native surface already selected a review target, reuse it instead of resolving a different scope.

Remain read-only. Do not edit, format, generate, stage, commit, push, post review comments, or open a pull request. A later request to fix findings is a separate execution task.

Read [review-contract.md](references/review-contract.md) before launching review lanes or assigning priorities.

## Resolve the review scope

1. Prefer the user's explicit files, commit, base branch, checked-out PR-style target, or review criteria. Review a remote PR only when it is already readable through configured GitHub tooling; otherwise return the access gap as `INCONCLUSIVE`.
2. Otherwise use the target selected by the native review surface.
3. Otherwise review all current changes: staged, unstaged, and untracked files. Do not assume ordinary `git diff` includes all three.
4. Read applicable `AGENTS.md`, linked review guidance, requirements, tests, and nearby implementation needed to understand the change.
5. Record the resolved base and head or the exact file set. State exclusions and unreadable artifacts before reviewing.
6. For a Git change review, capture the initial working-tree status. For a file audit outside Git, use canonical selected paths and captured bytes as the integrity baseline. Never revert user changes.

Classify the scope as either a **change review** or **file audit**. In a change review, find issues introduced or materially exposed by the selected change. In a file audit, inspect the complete selected-file contents and accept actionable defects contained in those files without inventing a historical baseline. Use surrounding code for context, but do not turn either mode into a general audit of unrelated code.

## Collect evidence

Inspect the raw diff and changed files before delegating. Include staged and untracked content when they belong to the scope. Use read-only history, search, and blame only when they materially clarify intent or regression risk.

Capture one content-pinned review snapshot in the parent context before launching lanes. Use the recipe that matches the selected target; ambient worktree changes never substitute for the requested target:

- **current changes** — current `HEAD`, exact staged and unstaged tracked diff bytes, and a canonical serialization of each untracked path's normalized relative path, file type, executable mode bits, symlink target when applicable, and complete content or explicit binary hash
- **commit** — selected commit and parent identifiers, the exact selected commit patch or changed tree bytes including binary content, and no unrelated current-worktree changes
- **base branch or checked-out PR-style target** — resolved merge base and head identifiers plus the exact range diff or changed tree bytes, with ambient current-worktree state recorded separately rather than injected into scope
- **file audit** — canonical selected paths plus each selected entry's file type, executable mode bits, symlink target when applicable, and complete file bytes or explicit binary hashes, including a clear unreadable-file record; Git is optional
- a deterministic fingerprint over the selected identifiers and captured bytes

Pass identical captured bytes, expected digest, and scope mode to both lanes. A file list or live-worktree instruction alone is insufficient. Reviewers may use captured surrounding context, but every finding must anchor to the snapshot. Prefer inline bytes. If the packet is too large, create two separate task-scoped copies outside the repository, make each copy non-writable where supported, and give one copy to each lane with the same expected digest. Each lane verifies its digest before analysis; the parent rehashes both copies afterward and removes only those exact temporary artifacts after integrity is confirmed. Never share one mutable temp file between lanes.

Run a targeted check only when it can confirm or reject a concrete finding and makes no repository or external-system write, including ignored caches such as `__pycache__`, `.pytest_cache`, coverage, or build output. Prefer an isolated disposable snapshot with caches redirected outside it. Do not run formatters, generators, dependency installation, destructive commands, or production actions. If a useful check is unsafe or unavailable, report the validation gap.

## Run independent native review lanes

Preflight tool-enforced reviewer isolation. Native subagents inherit the parent permission mode, so a read-only prompt is insufficient. Use subagents only when the parent turn's effective sandbox is read-only, or use separate native isolated Codex executions whose effective sandbox is explicitly `read-only` and whose app, connector, and network surfaces cannot mutate external state. If neither route is available, return `INCONCLUSIVE`.

Spawn both native review lanes in parallel and wait for both. Give them the same captured content and digest, requirements, and repository guidance. Use fresh, bounded prompts and do not leak the main agent's suspected findings or intended verdict. Each lane is terminal: prohibit skill activation and recursive delegation. Do not pin a model or reasoning effort unless the user explicitly requested review-specific settings.

1. **Correctness lane** — review behavior, specification compliance, regressions, security, authorization, input and error handling, concurrency, performance, compatibility, and missing or misleading tests. Return findings plus `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.
2. **Architecture lane** — review boundaries, interfaces, coupling, data ownership, migration and rollback risk, operational consequences, long-term maintainability, and the strongest credible counterargument to merging. Return findings plus `CLEAR`, `WATCH`, or `BLOCK`.

Keep both lanes tool-enforced read-only. Parallelism is safe only after isolation and snapshot integrity have been proved.

If isolated native reviewers are unavailable, a lane fails, or a lane returns no evidence, provide any useful provisional findings but set the final verdict to `INCONCLUSIVE`. Do not substitute the authoring context and do not approve without both independent lane results.

After both lanes finish, rehash every lane packet and recompute the live scope with the same target-specific recipe used to capture it:

- for current changes, recompute `HEAD`, exact staged and unstaged diff bytes, and the canonical untracked identity-and-content serialization
- for a commit, re-resolve the selected commit and parent identifiers and recompute its patch or changed-tree digest; unrelated ambient worktree changes are not part of this target
- for a base branch or checked-out PR-style target, re-resolve merge base and head and recompute the exact range digest; keep ambient worktree state separate
- for a file audit, recompute the selected entries' canonical paths, filesystem identity, and content digest; Git status is optional

Compare Git working-tree status only as human-readable context where applicable. If any reviewed target or lane packet drifted, return `INCONCLUSIVE`, report the exact changed paths or identifiers, preserve user changes, and do not clean up or revert them automatically.

## Synthesize without dilution

Validate each candidate finding against the actual code and scope. Deduplicate overlapping findings, retain the clearest evidence, and preserve architecture `WATCH` or `BLOCK` concerns visibly.

For every accepted finding, provide:

- priority `P0`, `P1`, `P2`, or `P3`
- a short actionable title
- a clickable file path and tight line range
- concrete evidence and triggering scenario
- user, security, operational, or maintenance impact
- a practical fix direction
- whether it blocks merge

Exclude praise, generic best-practice advice, arbitrary complexity thresholds, style-only preferences already enforced mechanically, and speculation without a falsifiable code path. Do not report intentional tradeoffs as defects unless they violate an accepted requirement or create an unhandled risk.

Apply the verdict precedence in [review-contract.md](references/review-contract.md) exactly. `APPROVE` means no actionable issue was found within the reviewed scope and available evidence; it is not proof of absolute correctness.

## Return the review

Lead with findings ordered by priority and impact. If there are no findings, say so explicitly. Then report:

1. architecture watchlist
2. correctness recommendation and architecture status
3. final verdict
4. reviewed scope, checks run, and validation gaps

When the active client supports native inline code comments, attach actionable findings to the tightest relevant lines and keep the final synthesis concise. Do not post the review to GitHub or another external system unless the user explicitly asks for that separate action.
