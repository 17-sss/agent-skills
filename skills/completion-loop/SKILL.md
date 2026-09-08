---
name: completion-loop
description: Complete approved implementation or fixes within frozen scope using risk-tiered verification, reusable evidence, and focused repair. Use $completion-loop to execute an approved plan or a clearly authorized small change; do not turn brainstorming, research, plan-only requests, or usage questions into implementation.
---

# Completion Loop

## Enter only for approved execution

This is an execution skill for completing approved implementation or fixes. It fits after investigation and plan approval. A request to think, research, write only a plan, or explain usage remains in that phase even if it mentions this skill. Approval to write a plan is not approval to execute it.

Reuse an approved plan's relevant scope, decisions, and completion criteria; inspect the current repository to confirm they still apply instead of replanning from scratch. A clearly authorized small fix needs no separate planning ceremony: capture a concise execution contract with the fields below. Resolve only missing decisions that materially affect scope, acceptance, or authority.

Approved-plan invocation: `/goal Implement the approved plan within its scope and completion criteria. Use $completion-loop.`

Small-fix invocation: `Use $completion-loop to fix the reproduced cache-key bug and verify it with the existing regression test. Keep public behavior unchanged.`

Skill activation alone does not authorize goal creation, a mode switch, commits, or remote work. Honor authority already granted in the conversation; do not request it again.

Read [verification-contract.md](references/verification-contract.md) before starting the execution loop. Read [browser-verification.md](references/browser-verification.md) only when browser or rendered evidence is required.

## Freeze the completion contract

1. Read the active Codex goal when Goal mode and goal tools are available.
2. Create a goal only when the user or system explicitly requested goal tracking and no active goal exists. Skill activation alone is not authorization to create one.
3. Inspect applicable repository instructions, current implementation, tests, and working-tree status. Preserve unrelated user changes.
4. Reference the approved plan where available and freeze this contract before editing; a small fix may use a compact block rather than a new plan document:

   - **Objective**
   - **In scope**
   - **Non-goals**
   - **Deployment target**
   - **Acceptance criteria**
   - **Required evidence**
   - **Risk tier** — `Low`, `Medium`, or `High`, with a short rationale
   - **Authorized repositories and external systems**

5. Resolve ambiguity that could materially change the contract. When a field is not part of the request, record `none`, `not authorized`, or `not part of this task` instead of silently widening it.
6. Freeze the contract once implementation begins. Do not automatically add newly suggested requirements, repositories, deployment paths, or external systems.

If Goal mode is unavailable, keep the same frozen contract in the current task context and state that cross-turn automatic continuation is not guaranteed.

## Execute the evidence loop

Repeat while a concrete in-scope action can advance an unmet acceptance criterion:

1. Choose the smallest meaningful incomplete requirement.
2. Investigate the current behavior and likely cause.
3. Implement the bounded change.
4. Run the smallest relevant check that can prove or disprove the change.
5. Inspect the decisive output and enough surrounding logs to establish the result; preserve necessary raw logs without repeatedly loading the same large logs or images.
6. If the check fails, distinguish a product defect, test/fixture error, or execution-environment error before choosing a repair or retry.
7. Update the existing task-local evidence ledger defined in the verification contract; do not create a parallel tracking system.
8. During edits, use relevant checks first; on a stable candidate, run required final verification. Thereafter rerun failed or invalidated checks. Expand coverage for shared dependencies or an uncertain impact boundary.

Change strategy when the same failure recurs. Do not delete valid tests, weaken acceptance criteria, repeat an unchanged check without an invalidation reason or an explicit repetition requirement, or claim that unexecuted checks “should” pass.

For expensive checks, record expected cost and a diagnosis checkpoint in the ledger. A budget overrun triggers strategy or scope review, never completion. Keep elapsed time, CPU time, and model token usage distinct; use measured usage when available and label estimates. Do not repeatedly poll unchanged progress or reload the same evidence just to reassure yourself.

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
- **Final full verification: at most one** initial run on the stable candidate after targeted evidence and required review findings are clear. Later runs cover only failed or invalidated ledger entries; broad invalidation can require the whole suite again.
- Do not repeat an identical full review packet or unchanged validation merely to seek a different answer.
- Allow one additional full-scope review only when the current work genuinely changes a core architecture boundary such as authentication, database authorization, or a public API contract. Record the reason and apply the material-expansion checkpoint when that change was not already in scope.

After a focused rereview, classify every new finding again:

- a regression created by the repair remains a blocker;
- a pre-existing issue that fails an acceptance criterion remains a blocker;
- an issue outside the frozen contract is deferred;
- an ambiguous issue requires user confirmation, not automatic expansion.

An implementation change invalidates only evidence and review conclusions whose recorded invalidation conditions intersect the changed boundary. It does not automatically reset the entire review.

Changes to shared dependencies, fixtures, renderer, host, build, environment, or baseline branch can invalidate broader evidence even when the edited source file is small. Revalidate the whole required suite if the impact cannot safely be narrowed. Explicit coverage, visual-review counts, consecutive-pass requirements, and mandatory independent review survive cost optimization.

When an independent review is required, run it through a tool-enforced read-only execution that cannot mutate the workspace or external systems. Keep it terminal and prevent recursive delegation. If that capability is unavailable, report the missing required evidence and request the minimum user decision needed; do not pretend the review occurred. If the user explicitly invokes a separate review workflow, follow that workflow's stricter contract without making it a dependency of this package.

## Pause at material expansion

Use the [material expansion checkpoint](references/verification-contract.md#material-expansion-checkpoint) when repeated review introduces new blocker categories, effort grows materially, or a repository, resource, deployment, service, migration, API, or queue boundary must expand. Present the proposed delta and smallest alternatives; do not implement expanded work before approval.

## Audit and finish

End the loop when:

1. every acceptance criterion has an implementation artifact and valid evidence;
2. all checks required by the risk tier pass or the user explicitly accepts a recorded contract revision for a gap; an unavailable check never becomes a pass;
3. no current-scope blocker remains;
4. final diff and working-tree status are understood and unrelated changes are preserved; and
5. deferred observations and residual risks are recorded for handoff or the final report.

Additional optimization, unused deployment paths, future automation, non-blocking architecture watch items, and unapproved expansion proposals do not prevent completion.

Distinguish **implementation complete**, **integration verification in progress**, and **awaiting real-device verification**. Testing an earlier phase's feature in integration does not mean that phase is being reimplemented. A missing required environment leaves verification pending. Separate local completion from pre-publication real-device validation only if the approved contract already defines those gates; do not invent that split to finish early.

Mark an active goal complete only after this audit passes. Follow the native blocked-state contract when a genuine blocker recurs; do not mark blocked merely because user confirmation is pending.

## Batch documentation and authorized commits

Do not create a commit unless the user authorized it. When commits are authorized, prefer stable boundaries for product/runtime implementation, tests/contracts, and deployment/docs. Combine consecutive fixes with the same cause instead of committing every review adjustment.

Keep intermediate notes in the existing ledger concise. At a stable point, consolidate relevant conclusions into the task's authorized owning documentation. Update HANDOFF or project history only when separately requested by the user; completion, transfer, or skill invocation does not grant that authority. When a handoff update is authorized, refresh it at a stable checkpoint, before transfer, or at final completion. Do not update it after every small repair.

## Return a concise completion report

Report only:

- implementation result and current verification status
- verification executed or reused, with remaining required environments
- remaining blockers, if any
- deferred items and residual risks
- commits created
- push, PR, and deploy status
- next work that requires additional approval

Do not narrate every internal review iteration.
