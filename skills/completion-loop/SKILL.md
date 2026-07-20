---
name: completion-loop
description: Drive a clearly scoped coding goal through investigation, implementation, evidence-based verification, and repair until its acceptance criteria are met or a genuine blocker is identified. Use when the user invokes $completion-loop or asks Codex to persist, finish, keep going, or not stop before verified completion; prefer Codex Goal mode for durable work.
---

# Completion Loop

Recommended invocation: `/goal <outcome, constraints, and verification criteria>. Use $completion-loop.`

Read [verification-contract.md](references/verification-contract.md) before starting the execution loop.

## Establish the completion contract

1. Read the active Codex goal when Goal mode and goal tools are available.
2. Create a goal only when the user or system explicitly requested goal tracking and no active goal exists. Skill activation alone is not authorization to create one.
3. State the desired outcome, constraints, acceptance criteria, and the commands or observations that can prove completion.
4. Inspect applicable repository instructions, current implementation, tests, and working-tree status. Preserve unrelated user changes.
5. Resolve material ambiguity before editing. Do not silently narrow the goal to make it easier.

If Goal mode is unavailable, keep the same completion contract in the current task context and state that cross-turn automatic continuation is not guaranteed.

## Execute the evidence loop

Repeat while a concrete next action can advance the accepted goal:

1. Choose the smallest meaningful incomplete requirement.
2. Investigate the current behavior and likely cause.
3. Implement the bounded change.
4. Run the smallest relevant check that can prove or disprove the change.
5. Read the complete failure or success output.
6. If the check fails, explain the cause it reveals and use that evidence to choose the next change.
7. Expand verification from targeted tests to applicable typecheck, lint, build, integration, and runtime checks in proportion to risk.

Change strategy when the same failure recurs. Do not simulate persistence with arbitrary iteration counts, delete valid tests, weaken acceptance criteria, or claim that unexecuted checks “should” pass.

The request to keep going does not authorize destructive actions, external production changes, credential use, or material scope expansion. Obtain the authority those actions normally require.

## Run the independent completion review

Before completing any goal that changed implementation artifacts, require a fresh independent Codex reviewer. Scale the review depth for large, security-sensitive, architectural, difficult-to-test, or otherwise high-risk diffs, but do not skip the independent gate for a small change.

The implementation turn is normally writable, and native subagents inherit that permission mode. A read-only prompt is therefore not a safety boundary. Run the reviewer only through a native isolated Codex execution whose effective sandbox is explicitly `read-only` and whose app, connector, and network surface cannot mutate external state. A local Codex CLI may satisfy this with an ephemeral execution explicitly configured with `--sandbox read-only`; do not install or reconfigure Codex to create this gate. The reviewer is a terminal lane and must not activate another workflow or delegate recursively. If enforced isolation is unavailable, the independent gate is unavailable and the goal cannot be marked complete.

- Capture one candidate-state fingerprint from the current `HEAD`, exact staged and unstaged diff bytes, and a canonical serialization of each untracked path's file type, executable mode bits, symlink target when applicable, and content or content hash.
- Provide the reviewer with the requirements, captured raw diff or changed-file bytes, verification output, and that fingerprint. Prefer passing captured bytes directly; do not instruct the reviewer to derive the candidate from a changing live worktree.
- Do not provide the leader's conclusion, suspected answer, or intended verdict.
- Require blocking findings, coverage gaps, residual risks, and confidence.
- Recompute the fingerprint when the reviewer returns. If it changed during review, report the unexpected mutation, preserve the files, and do not reuse that review result.
- Fix blocking findings and rerun affected verification. Any implementation-artifact change after review invalidates the prior result; obtain a fresh independent review of the new candidate state before completion.

When an isolated reviewer is unavailable, perform an explicit self-review for useful provisional evidence, report the missing independent gate, and do not mark the goal complete until an independent result is available.

## Audit completion

Before declaring completion:

1. Re-read the active goal or completion contract.
2. Inspect the final diff and working-tree status, and confirm they still match the independently reviewed candidate fingerprint.
3. Map every requirement to its implementation artifact and fresh evidence.
4. Confirm that no required task remains pending and no validation failure is being ignored.
5. Record skipped checks and residual risks explicitly.
6. Mark the active goal complete only after this audit passes and no required work remains.

Do not treat one passing test, a successful build, or reviewer approval as proof of the whole objective unless it covers every acceptance criterion.

## Handle blockers honestly

Exhaust safe in-scope alternatives before stopping. Report:

- the exact blocking condition
- evidence that it blocks the accepted goal
- alternatives already attempted
- the minimum user decision, authority, credential, or external-state change needed

Difficulty, slow progress, uncertainty, or a failing check is not by itself a blocker. When Goal mode defines a blocked-state threshold, follow that tool contract; do not mark blocked early. In environments that require recurrence across goal turns, wait until the same condition has met that recurrence rule.
