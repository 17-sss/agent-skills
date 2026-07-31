# Completion Loop Verification Contract

Use this contract to preserve completion quality without turning review observations into an unbounded project.

## Frozen completion contract

Record this task-local block before implementation:

| Field | Required content |
| --- | --- |
| Objective | One testable outcome |
| In scope | Behaviors, components, and files that may change |
| Non-goals | Explicit exclusions and tempting adjacent work |
| Deployment target | The environment that must actually run this result |
| Acceptance criteria | Observable pass conditions |
| Required evidence | Commands or observations that prove those conditions |
| Risk tier | `Low`, `Medium`, or `High`, with rationale |
| Authorized repositories and external systems | Exact writable scope; use `none` when no external mutation is authorized |

Freeze the block when implementation begins. A later discovery may invalidate an assumption, but it does not silently become a requirement. Revise the contract only after the user approves a material expansion.

## Finding classification

Accept a finding as a current blocker only when it has reproducible evidence and one of these contract relationships:

| Classification test | Result |
| --- | --- |
| Fails a stated acceptance criterion | Blocker |
| Current implementation or repair creates a regression | Blocker |
| Creates a security vulnerability, data loss, authorization bypass, or service outage on an in-scope path | Blocker |
| Makes the declared deployment target unable to run | Blocker |
| Pre-existing issue that does not fail an acceptance criterion | Deferred |
| Future scale, convenience, observability, or product enhancement | Deferred |
| Unused deployment or infrastructure path | Deferred |
| Relationship to the frozen contract is ambiguous | User checkpoint |

Default these observations to `Deferred / Follow-up / Residual risk`:

- future expansion work;
- Docker, Kubernetes, ECS, Fargate, or another deployment path not named in the contract;
- operational convenience automation;
- a separate backup scheduler;
- host firewall automation;
- additional monitoring or dashboards;
- speculative throughput optimization;
- code-style preference;
- unrelated legacy defects; and
- new product functionality.

A local-only goal treats a Kubernetes-readiness finding as deferred. An `EC2 + Docker Compose` goal does not review Kubernetes manifests or AWS Batch configuration. A `Vercel UI + EC2 worker` goal does not move crawler execution into Vercel. A minimal-deployment goal does not add systemd, host-firewall automation, or a backup scheduler unless explicitly required.

## Material expansion checkpoint

Pause implementation and request approval to revise the frozen contract when:

1. two consecutive review passes introduce a new blocker category;
2. a new repository or cloud resource is needed;
3. the deployment method changes;
4. a new operational service is proposed;
5. expected effort or change volume grows materially; or
6. a migration, API, or queue contract needs redesign.

Show the current contract, proposed delta, evidence, impact, and smallest in-scope alternative. Waiting for that decision is not permission to implement the expansion and is not, by itself, a native blocked-state verdict.

## Evidence matrix and ledger

Map each accepted requirement before completion:

| Requirement | Implementation artifact | Verification | Fresh result | Residual risk |
| --- | --- | --- | --- | --- |
| `<criterion>` | `<file, symbol, behavior, or external artifact>` | `<command or observation>` | `<pass, fail, or unavailable with reason>` | `<none or explicit gap>` |

Keep a task-local evidence ledger:

| Command or observation | Target commit or worktree fingerprint | Affected scope | Result | Invalidation condition |
| --- | --- | --- | --- | --- |
| `<exact check>` | `<commit or deterministic fingerprint>` | `<files and behavior>` | `<pass/fail plus decisive output>` | `<which later changes require rerun>` |

A command name without fresh output is not evidence. Do not rerun an unchanged test when the target fingerprint, affected scope, and invalidation condition show that its result remains valid. During repair, run targeted checks. Run the risk-tier final suite or build once on the final candidate; if it fails, preserve unaffected ledger entries and rerun only failed or invalidated checks after the fix.

## Risk-tiered verification

Choose the lowest tier that honestly covers the frozen change:

| Tier | Required verification |
| --- | --- |
| Low | Targeted tests, applicable typecheck or lint, and self-review of the diff |
| Medium | Targeted tests, relevant integration tests, final build, and one focused independent review |
| High | Full contract tests, real E2E, security/authorization/data-integrity checks, and independent correctness plus architecture review |

Escalate the tier when evidence shows the original choice was wrong; record the reason. Do not apply the High tier to every task. If the user explicitly invokes another review workflow, its stricter verification contract takes precedence.

## Frozen independent-review packet

Every independent lane receives the same content-pinned packet:

- exact `base...HEAD` range, plus a canonical staged, unstaged, and untracked overlay when the candidate is not fully committed;
- one deterministic packet digest;
- objective, requirements, and acceptance criteria;
- non-goals;
- actual deployment target;
- risk tier and required evidence;
- fresh verification logs; and
- known existing failures and unavailable environments.

Do not give a reviewer the desired verdict or leader diagnosis. Require reproducible blockers, coverage gaps, deferred observations, residual risks, and confidence. Include this exact boundary:

> Do not invent requirements. Findings outside the frozen completion contract must be reported as deferred observations, not blockers.

Correctness and architecture lanes may be separate, but both must use the same packet and digest. Recompute the candidate fingerprint after review. Adopt a finding only after reproducing it in the actual code and mapping it to the frozen blocker definition.

## Review budget and focused rereview

- Spend at most one initial full-scope review on the first candidate.
- After an accepted blocker is fixed, review only its cause, modified files, directly connected call path, new regression tests, and plausible adjacent regressions.
- Do not rescan the already-passed codebase or seek another verdict on the same packet.
- Allow one additional full-scope review only for a recorded core-architecture change. If that change is outside the frozen contract, obtain expansion approval first.
- Spend at most one final full verification after focused checks and review blockers are clear.

During focused rereview, keep a regression introduced by the current fix as a blocker. Keep a pre-existing issue as a blocker only when it fails an acceptance criterion. Defer findings outside the frozen contract. Escalate ambiguous classification to the user instead of expanding automatically.

## Dirty worktree discipline

Record the initial status and a content fingerprint over `HEAD`, staged and unstaged diff bytes, and a canonical serialization of untracked path names, file types, executable mode bits, symlink targets, and content hashes. Separate pre-existing changes from workflow changes and avoid touching unrelated files. Review the final diff against that baseline before completion.

## Commit and handoff discipline

Skill activation does not authorize a new thread, commit, push, PR, or deployment. When the user authorizes commits, prefer stable boundaries:

1. product or runtime implementation;
2. tests and contracts; and
3. deployment and documentation.

Combine consecutive corrections with the same cause. Do not commit each small review hardening separately. Refresh a handoff only at a stable checkpoint, immediately before transfer, or at final completion.

## Completion evidence

Completion requires satisfied acceptance criteria, required verification, zero current-scope blockers, understood worktree state, and recorded deferred observations. Optional optimization, unused deployment improvements, future operational automation, non-blocking architecture watch items, and unapproved expansion do not block completion.
