# Completion Loop Verification Contract

Use this contract to prevent partial completion and evidence-free claims.

## Evidence matrix

Build a task-local matrix before completion:

| Requirement | Implementation artifact | Verification | Fresh result | Residual risk |
| --- | --- | --- | --- | --- |
| `<criterion>` | `<file, symbol, behavior, or external artifact>` | `<command or observation>` | `<pass, fail, or unavailable with reason>` | `<none or explicit gap>` |

Every accepted requirement needs an artifact and evidence. A command name without fresh output is not evidence.

## Select verification proportionally

- Use focused unit or regression tests for local behavior.
- Use typecheck and static analysis for type or contract changes.
- Use lint or format checks when the change crosses those rules.
- Use integration tests for boundaries between modules, services, storage, or APIs.
- Use build checks for bundling, generation, and deployment-shape changes.
- Use runtime or browser smoke checks for behavior that static checks cannot prove.
- Use security, migration, rollback, or data-integrity checks when the risk requires them.

Start with the smallest discriminating check, then broaden enough to cover the changed boundary.

## Read failures

Record the failing command, exit status, decisive output, and what it disproves. Change the next hypothesis or action. Repeating the same command without a reason is not an iteration.

## Reviewer contract

The reviewer must run under a tool-enforced Codex `read-only` sandbox. Native subagents inherit the writable implementation turn, so instructions alone are insufficient. Use a separate native isolated Codex execution with an explicitly read-only effective sandbox and no state-changing app or connector tools. This is a terminal lane: it must not activate another workflow or delegate recursively. If that route is unavailable, independent approval is unavailable.

Give an independent reviewer:

- the requirements and constraints
- the raw final diff or changed files
- fresh verification logs
- known unavailable environments
- a deterministic fingerprint of the candidate state

Do not give the reviewer the desired verdict or leader diagnosis. Ask for blocking findings, missing coverage, residual risks, and confidence.

Recompute the candidate fingerprint after review as defense in depth. Treat any reviewer-time drift as an invalid review result. If the leader changes implementation artifacts to address a finding, rerun affected checks and obtain a fresh reviewer result for the new fingerprint; approval never carries forward across code changes.

## Dirty worktree discipline

Record the initial status and a content fingerprint over `HEAD`, staged and unstaged diff bytes, and a canonical serialization of untracked path names, file types, executable mode bits, symlink targets, and content hashes. Separate pre-existing changes from changes made by this workflow and avoid touching unrelated files. Review the final diff against that baseline before completion.

## Blocker evidence

A blocker report must identify the exact external dependency, missing authority, credential, user decision, or state change; show attempts and safe alternatives; and state the minimum action needed to resume.
