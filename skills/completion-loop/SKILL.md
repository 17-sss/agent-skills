---
name: completion-loop
description: Drive a frozen, clearly scoped coding goal through investigation, implementation, risk-tiered verification, focused repair, and evidence-based completion without absorbing unrelated follow-up work. Use when the user invokes $completion-loop or asks Codex to persist, finish, keep going, or not stop before verified completion; prefer Codex Goal mode for durable work.
---

# Completion Loop

Recommended invocation: `/goal <outcome, constraints, deployment target, and verification criteria>. Use $completion-loop.`

Read [verification-contract.md](references/verification-contract.md) before starting the execution loop.

## Freeze the completion contract

1. Read the active Codex goal when Goal mode and goal tools are available.
2. Create a goal only when the user or system explicitly requested goal tracking and no active goal exists. Skill activation alone is not authorization to create one.
3. Write and freeze this contract before editing:

   - **Objective**
   - **In scope**
   - **Non-goals**
   - **Deployment target**
   - **Acceptance criteria**
   - **Required evidence**
   - **Risk tier** — `Low`, `Medium`, or `High`, with a short rationale
   - **Authorized repositories and external systems**

4. Inspect applicable repository instructions, current implementation, tests, and working-tree status. Preserve unrelated user changes.
5. Resolve ambiguity that could materially change the contract. When a field is not part of the request, record `none`, `not authorized`, or `not part of this task` instead of silently widening it.
6. Freeze the contract once implementation begins. Do not automatically add newly suggested requirements, repositories, deployment paths, or external systems.

If Goal mode is unavailable, keep the same frozen contract in the current task context and state that cross-turn automatic continuation is not guaranteed.

## Execute the evidence loop

Repeat while a concrete in-scope action can advance an unmet acceptance criterion:

1. Choose the smallest meaningful incomplete requirement.
2. Investigate the current behavior and likely cause.
3. Implement the bounded change.
4. Run the smallest relevant check that can prove or disprove the change.
5. Read the complete failure or success output.
6. If the check fails, record what it disproves and use that evidence to choose the next change.
7. Update the task-local evidence ledger defined in the verification contract.
8. Broaden checks only as required by the frozen risk tier and changed boundary.

Change strategy when the same failure recurs. Do not delete valid tests, weaken acceptance criteria, repeat an unchanged check without an invalidation reason, or claim that unexecuted checks “should” pass.

The request to keep going does not authorize destructive actions, commits, new threads, external production changes, credential use, or material scope expansion. Obtain the authority those actions normally require.

## Classify findings against the frozen scope

Adopt a newly discovered issue as a current blocker only when evidence shows that it:

- fails an acceptance criterion;
- is a regression created by the current change;
- creates a security vulnerability, data loss, authorization bypass, or service outage on a path used by the frozen contract; or
- makes execution impossible on the declared deployment target.

Classify future expansion, unused deployment paths, operational convenience work, unrelated legacy defects, style preferences, and new product features as `Deferred / Follow-up / Residual risk`. A reviewer cannot expand the contract.

Evaluate only the declared deployment target. Do not add container platforms, cloud services, schedulers, firewall automation, monitoring, backup systems, or other operational infrastructure unless the frozen contract requires them.

Give every reviewer this instruction:

> Do not invent requirements. Findings outside the frozen completion contract must be reported as deferred observations, not blockers.

Reproduce each proposed blocker against the actual code and contract before accepting it. When classification is ambiguous, stop before implementation and ask the user whether to revise the frozen contract.

## Spend the review and verification budget

Use the risk-tier matrix and review packet in the verification contract.

- **Initial full-scope review: at most one.** Use the frozen packet and the review depth required by the risk tier.
- **Blocker repair: focused rereview only.** Recheck the finding's cause, modified files, directly connected call paths, new regression tests, and plausible adjacent regressions.
- **Final full verification: at most one.** Run it only after targeted evidence and required review findings are clear. If it fails, rerun only failed or invalidated ledger entries after repair.
- Do not repeat an identical full review packet or unchanged validation merely to seek a different answer.
- Allow one additional full-scope review only when the current work genuinely changes a core architecture boundary such as authentication, database authorization, or a public API contract. Record the reason and apply the material-expansion checkpoint when that change was not already in scope.

After a focused rereview, classify every new finding again:

- a regression created by the repair remains a blocker;
- a pre-existing issue that fails an acceptance criterion remains a blocker;
- an issue outside the frozen contract is deferred;
- an ambiguous issue requires user confirmation, not automatic expansion.

An implementation change invalidates only evidence and review conclusions whose recorded invalidation conditions intersect the changed boundary. It does not automatically reset the entire review.

When an independent review is required, run it through a tool-enforced read-only execution that cannot mutate the workspace or external systems. Keep it terminal and prevent recursive delegation. If that capability is unavailable, report the missing required evidence and request the minimum user decision needed; do not pretend the review occurred. If the user explicitly invokes a separate review workflow, follow that workflow's stricter contract without making it a dependency of this package.

## Pause at material expansion

Stop implementation and ask whether to revise the frozen contract when any of these occurs:

- two consecutive review passes discover a new blocker category;
- a new repository or cloud resource is required;
- the deployment method must change;
- an operational service absent from the contract must be added;
- expected change volume or effort grows materially beyond the initial plan; or
- a migration, API, or queue contract must be redesigned.

Present the proposed contract delta, evidence, impact, and smallest alternatives. Do not implement the expanded work before the user approves it.

## Audit and finish

End the loop when:

1. every acceptance criterion has an implementation artifact and valid evidence;
2. all checks required by the risk tier pass or have an explicitly accepted gap;
3. no current-scope blocker remains;
4. final diff and working-tree status are understood and unrelated changes are preserved; and
5. deferred observations and residual risks are recorded for handoff or the final report.

Additional optimization, unused deployment paths, future automation, non-blocking architecture watch items, and unapproved expansion proposals do not prevent completion.

Mark an active goal complete only after this audit passes. Follow the native blocked-state contract when a genuine blocker recurs; do not mark blocked merely because user confirmation is pending.

## Batch commits and handoffs

Do not create a commit unless the user authorized it. When commits are authorized, prefer stable boundaries for product/runtime implementation, tests/contracts, and deployment/docs. Combine consecutive fixes with the same cause instead of committing every review adjustment.

Refresh a handoff only at a stable checkpoint, immediately before transferring work, or at final completion. Do not update it after every small repair.

## Return a concise completion report

Report only:

- implementation result
- verification executed
- remaining blockers, if any
- deferred items and residual risks
- commits created
- push, PR, and deploy status
- next work that requires additional approval

Do not narrate every internal review iteration.
