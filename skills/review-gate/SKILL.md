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
6. For a Git change review, capture the initial working-tree status. For a file audit outside Git, use canonical selected paths and a parent-held original-target fingerprint as the integrity baseline. Never revert user changes.

Classify the scope as either a **change review** or **file audit**. In a change review, find issues introduced or materially exposed by the selected change. In a file audit, inspect the screened selected-file projection and accept actionable defects supported by that evidence without inventing a historical baseline. Use screened surrounding code for context, but do not turn either mode into a general audit of unrelated code.

## Protect sensitive review material

Never place credential values, private keys, session tokens, authenticated configuration, or other sensitive values in prompts, model-visible output, reviewer packets, temporary copies, or the final report. A code review can identify that sensitive material exists without reproducing its value.

Before building a review packet:

1. Screen candidate paths and text with non-echoing local checks. Treat private-key blocks, credential files, non-placeholder `.env` values, access tokens, cookies, and similarly authenticated material as sensitive. Treat an uncertain candidate as sensitive.
2. Keep the original target in place and compute its integrity fingerprint locally in the parent context. Do not copy, print, or forward a sensitive value merely to prove snapshot integrity.
3. Build a review projection. Preserve text that passes the sensitivity screen; replace each sensitive span with a structural marker that records only its category and location, never its value or a value-derived hash. Represent non-sensitive binary content with path, file identity, size, and a content digest. For sensitive or wholly withheld content, include only path, file identity, size, and the withholding reason; keep its digest inside the parent-only fingerprint.
4. Apply the same screen to surrounding context. When sensitive material exists, use reviewer lanes only if their filesystem and tool visibility is restricted to the sanitized packet. A prompt telling a lane not to open the workspace is not enforcement.
5. If redaction, a withheld file, or unavailable isolation removes evidence that could materially change a finding or verdict, return `INCONCLUSIVE` and name the validation gap without revealing the value. Never ask the user to paste a secret into the conversation.

## Collect evidence

Inspect the raw diff and changed files before delegating. Include staged and untracked content when they belong to the scope. Use read-only history, search, and blame only when they materially clarify intent or regression risk.

Capture one content-pinned review snapshot in the parent context before launching lanes. Use the recipe that matches the selected target and pass all review material through the sensitivity guard above; ambient worktree changes never substitute for the requested target:

- **current changes** — current `HEAD`, staged and unstaged tracked patch projections, and a canonical projection of each untracked path's normalized relative path, file type, executable mode bits, symlink target when applicable, and screened text or withheld-content record
- **commit** — selected commit and parent identifiers, its screened patch or changed-tree projection, binary and withheld-content records, and no unrelated current-worktree changes
- **base branch or checked-out PR-style target** — resolved merge base and head identifiers plus the screened range-diff or changed-tree projection, with ambient current-worktree state recorded separately rather than injected into scope
- **file audit** — canonical selected paths plus each selected entry's file type, executable mode bits, symlink target when applicable, and screened text or withheld-content record, including a clear unreadable-file record; Git is optional
- a parent-only fingerprint over the original local target and a separate deterministic digest over the sanitized lane packet

Pass the identical sanitized packet, packet digest, and scope mode to both lanes. Never forward the original target as prompt text. A file list or live-worktree instruction alone is insufficient. Reviewers may use screened surrounding context, but every finding must anchor to the packet. If the packet is too large, create two separate task-scoped copies outside the repository, make each copy non-writable where supported, and give one copy to each lane with the same expected digest. Each lane verifies its digest before analysis; the parent rehashes both copies afterward and removes only those exact temporary artifacts after integrity is confirmed. Never share one mutable temp file between lanes.

Run a targeted check only when it can confirm or reject a concrete finding and makes no repository or external-system write, including ignored caches such as `__pycache__`, `.pytest_cache`, coverage, or build output. Prefer an isolated disposable snapshot with caches redirected outside it. Do not run formatters, generators, dependency installation, destructive commands, or production actions. If a useful check is unsafe or unavailable, report the validation gap.

## Run independent native review lanes

Preflight tool-enforced reviewer isolation. Native subagents inherit the parent permission mode, so a read-only prompt is insufficient. Use subagents only when the parent turn's effective sandbox is read-only, or use separate native isolated Codex executions whose effective sandbox is explicitly `read-only` and whose app, connector, and network surfaces cannot mutate external state. If neither route is available, return `INCONCLUSIVE`.

Spawn both native review lanes in parallel and wait for both. Give them the same sanitized content projection and packet digest, requirements, and screened repository guidance. Use fresh, bounded prompts and do not leak the main agent's suspected findings or intended verdict. Each lane is terminal: prohibit skill activation and recursive delegation. Do not pin a model or reasoning effort unless the user explicitly requested review-specific settings.

1. **Correctness lane** — review behavior, specification compliance, regressions, security, authorization, input and error handling, concurrency, performance, compatibility, and missing or misleading tests. Return findings plus `APPROVE`, `COMMENT`, or `REQUEST_CHANGES`.
2. **Architecture lane** — review boundaries, interfaces, coupling, data ownership, migration and rollback risk, operational consequences, long-term maintainability, and the strongest credible counterargument to merging. Return findings plus `CLEAR`, `WATCH`, or `BLOCK`.

Keep both lanes tool-enforced read-only. Parallelism is safe only after isolation and snapshot integrity have been proved.

If isolated native reviewers are unavailable, a lane fails, or a lane returns no evidence, provide any useful provisional findings but set the final verdict to `INCONCLUSIVE`. Do not substitute the authoring context and do not approve without both independent lane results.

After both lanes finish, rehash every lane packet and recompute the live scope with the same target-specific recipe used to capture it:

- for current changes, recompute the parent-held original-target fingerprint from `HEAD` plus staged, unstaged, and untracked state, then regenerate the sanitized projection
- for a commit, re-resolve the selected commit and parent identifiers, recompute its parent-held target fingerprint, and regenerate the sanitized projection; unrelated ambient worktree changes are not part of this target
- for a base branch or checked-out PR-style target, re-resolve merge base and head, recompute the parent-held range fingerprint, and regenerate the sanitized projection; keep ambient worktree state separate
- for a file audit, recompute the selected entries' canonical paths, filesystem identity, parent-held content fingerprint, and sanitized projection; Git status is optional

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
