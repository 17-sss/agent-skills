---
name: milestone-runner
description: Turn a large, explicitly requested outcome into a durable repository-local sequence of goals, execute one goal at a time through native Codex Goal mode, checkpoint evidence, resume safely, and complete only after a final verification and review gate. Use when the user invokes $milestone-runner, asks for durable multi-goal execution, wants a long-running implementation broken into restartable stages, or needs repository-tracked progress without an external workflow runtime.
---

# Milestone Runner

Recommended invocation: `Use $milestone-runner to complete <outcome, constraints, and verification criteria>.`

Keep this package standalone. Do not invoke or require another skill. Use only native Codex goal tools, ordinary repository tools, an available native read-only reviewer, and this package's bundled state helper.

Read [state-contract.md](references/state-contract.md) before creating or changing durable goal state. Read [goal-state-cli.md](references/goal-state-cli.md) when constructing commands, handling a failure, or diagnosing recovery.

## Establish the durable plan

1. Inspect the applicable repository instructions, current implementation, tests, working-tree status, and any user-provided specification.
2. Resolve only ambiguity that would materially change scope, safety, architecture, or verification. Do not create state while the accepted outcome is still unclear.
3. Convert the accepted outcome into a small ordered list of independently verifiable goals. Every goal must include an objective, acceptance criteria, and concrete verification methods.
4. Select a stable kebab-case slug. Store state only under `.agent-workflows/goals/<slug>/` in the target repository. Do not use `.codex/` for mutable workflow data and do not create a state directory for workflows that do not need durable state.
5. Prepare the initialization JSON described in the state contract and run:

   ```text
   python3 <skill-dir>/scripts/goal_state.py --repo-root <repo> init --slug <slug> --spec <spec.json>
   ```

   Initialization must refuse to overwrite an existing plan. Inspect the generated `brief.md`, `goals.json`, and `ledger.jsonl` before implementation.

The explicit invocation of this skill, or a direct request for durable goal tracking, authorizes creating a native Codex goal when none exists. Call `get_goal` first. If no goal exists and goal tools are available, call `create_goal` with the exact `aggregate_goal` emitted by the state helper. If the user already started a semantically matching goal, keep it. If a different goal is active, stop without clearing or replacing it and report the conflict.

If native Goal mode is unavailable, the repository artifacts may still support manual resume in the current task, but automatic continuation is not guaranteed. State that limitation explicitly.

## Execute one goal at a time

Before every mutation, run `status` and pass its current `revision` back as `--expected-revision`. A revision mismatch means another writer changed the plan; re-read it instead of forcing an overwrite. Every locked command also validates and rolls forward a complete pending transaction left by an interrupted prior write.

For the first non-terminal goal:

1. Start only that goal with the helper's `start` command.
2. Re-read its objective, acceptance criteria, and verification methods.
3. Investigate and implement the smallest coherent change that can satisfy it. Preserve unrelated user changes and existing repository conventions.
4. Run targeted verification, then expand to applicable tests, typecheck, lint, build, integration, runtime, security, or visual checks in proportion to risk.
5. Record a completion evidence JSON and checkpoint `complete` only when every acceptance criterion is proved. The helper rejects evidence-free completion.
6. If genuinely blocked, record the exact blocker, attempted safe alternatives, and minimum needed action, then checkpoint `blocked`. Do not start a later goal while the earlier goal remains blocked.
7. Resume a blocked goal only after the blocking condition changes. Replace it only with an explicit evidence-backed replacement; never silently delete or weaken accepted work.

Use the bundled helper for `status`, `start`, `checkpoint`, `resume`, `append`, `replace`, and `validate`. It manages repository artifacts only. It never calls Codex goal tools, changes permissions, edits source files, installs dependencies, or touches external systems.

## Handle discoveries without plan drift

Append a new pending goal only when fresh evidence shows that additional work is required to satisfy the original objective. Record the reason. Replace a pending or blocked goal only when the replacement preserves the original constraints and verification strength.

Do not:

- reorder completed evidence to make the history look cleaner
- mark work complete from intention, partial output, or stale tests
- mutate the original objective or constraints merely to avoid a blocker
- let delegated workers own or edit `.agent-workflows/`
- run two writers against the same plan

Native subagents may perform bounded investigation, implementation, or review when useful, but the parent task remains the single owner of durable state and reconciles every returned result against current files and tests.

## Run the final quality gate

When every goal is `complete` or explicitly `superseded`:

1. Re-read the original objective, constraints, all acceptance criteria, and the full ledger.
2. Inspect the final diff and working-tree status.
3. Rerun the broadest applicable verification from a clean candidate state.
4. Map each requirement to implementation artifacts and fresh evidence.
5. For implementation changes, obtain a fresh independent Codex review under an effective read-only sandbox. Give it the accepted requirements, captured candidate bytes or diff, verification output, and a deterministic fingerprint. Do not leak the desired verdict. If an enforced read-only reviewer is unavailable, keep the run incomplete and report the missing gate.
6. Fix blocking findings, rerun affected checks, and repeat the independent review after every implementation change.
7. Build the final quality-gate JSON from the state contract. It must cover every objective, constraint, completed-goal acceptance criterion, and declared verification string using its exact text; additional fresh checks may also be recorded. Record whether implementation changed, the corresponding review result, and residual risks.
8. Only now call `update_goal` with `complete`. Immediately save the completed goal object from that successful tool result outside the repository or in a task-scoped temporary file. A later `get_goal` may return no active goal after completion; that does not replace the saved completion result.
9. Run `finalize` with the quality gate and saved completed goal object. The helper refuses finalization when goals, evidence, review, or native goal reconciliation are incomplete.

Do not mark a native goal blocked before the current goal-tool contract permits it. Local blocked evidence may remain in the ledger while the native goal stays active. Never clear a goal implicitly; goal clearing is an explicit user-facing action.

## Report the result

Return:

- the durable plan path and final status
- completed, superseded, or blocked goal IDs
- changed implementation artifacts
- verification and independent-review evidence
- residual risks and skipped checks
- the exact blocker and minimum next action when incomplete

Do not claim completion from the ledger alone. Repository state, fresh checks, independent review when required, and the native goal snapshot must agree.
