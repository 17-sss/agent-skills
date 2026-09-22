# Completion Loop Verification Contract

Use this contract to preserve completion quality without turning review observations into an unbounded project.

## Frozen completion contract

Record this task-local block before implementation. Reference relevant sections of an approved plan instead of copying or redesigning it. A clearly authorized small fix may use a few lines covering the same fields; absent deployment or external authority is `none`, not a new work item.

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

Extend the existing task-local evidence ledger; the requirement map may point to its entries instead of duplicating results. Do not introduce another journal, database, or workflow-state file just for this skill.

| Command or observation | Target and inputs | Affected scope | Result and artifact | Invalidation condition | Cost / diagnosis checkpoint |
| --- | --- | --- | --- | --- | --- |
| `<exact check and configuration>` | `<candidate fingerprint, input identities>` | `<requirements, files, consumers>` | `<pass/fail/unavailable, decisive output, raw log/capture path>` | `<changes or expiry that require rerun>` | `<estimate and when to diagnose; omit for cheap checks>` |

Record the code revision and dirty diff fingerprint (including untracked inputs), relevant shared dependency/lockfile versions, fixture/seed, build identity, runner/renderer, host/environment configuration, and baseline branch identity. Mark irrelevant inputs `n/a`; do not collect secrets or dump the entire environment. Keep identities lightweight using existing hashes, manifests, build IDs, or tool output. A commit ID alone does not identify a dirty candidate.

A command name without fresh output is not evidence. Do not rerun an unchanged test when the target fingerprint, affected scope, and invalidation condition show that its result remains valid. If the candidate changed, compare the delta with the recorded inputs and affected scope; retain a result only with a short non-invalidation reason. Missing identity, unexplained drift, or an uncertain impact boundary requires new evidence.

During repair, run targeted checks. Run the required risk-tier final suite or build on the stable candidate after required review blockers are clear. Preserve unaffected ledger entries and rerun only failed or invalidated checks after subsequent changes. Explicit repetitions, visual-review counts, and consecutive-pass conditions remain required observations; record their sequence and do not count one cached result as multiple passes.

| Change since the recorded check | Evidence decision |
| --- | --- |
| Documentation-only wording outside runtime/build/test inputs | Check relevant docs, links, or contracts; retain unaffected runtime evidence with the reason |
| One bounded behavior changes | Recheck that behavior and connected regressions; preserve demonstrably unaffected entries |
| Shared dependency, renderer, host, fixture, build configuration, or environment changes | Re-evaluate all consuming checks, including browser captures and integration results |
| Baseline branch moves | Recompute comparison and review scope; inspect the delta before retaining conclusions |
| Impact cannot safely be narrowed | Rerun the whole required suite; a prior full run is no exemption |

## Cost and failure diagnosis

Before an expensive build, matrix, or review, record expected elapsed/runtime cost, concurrency or resource demand when relevant, and a concrete diagnosis checkpoint such as a timeout, a stalled readiness signal, or recurrence of the same failure. Use existing runner deadlines and measured prior runs where available; do not add a profiling framework. At the checkpoint inspect progress and the failure class before choosing a changed retry strategy.

Wall-clock duration, CPU execution time, and model token usage are different quantities. Do not infer tokens from build duration or CPU load. Label estimated costs and unavailable measurements honestly. A cost overrun is a signal to reduce redundant work, change the execution strategy, or seek approval for a material contract change; it is never evidence of completion and does not waive mandatory checks.

Distinguish product defects from test/fixture errors and execution-environment errors using logs and the approved behavior. A faulty test may be corrected only with an independent basis for the expected behavior; record that basis and invalidate checks that depend on the changed test/fixture. Do not change expected values or tolerances merely to get green output, or repeat the same failure without new diagnostic evidence or a relevant change.

Preserve necessary original logs and captures at task-local artifact paths and keep decisive excerpts in the ledger. Read additional sections when needed for diagnosis or independent review; do not repeatedly send the same large logs or images to the model. Poll running work at bounded, useful checkpoints or use completion notifications instead of repeatedly rechecking unchanged progress.

## Risk-tiered verification

Choose the lowest tier that honestly covers the frozen change:

| Tier | Required verification |
| --- | --- |
| Low | Targeted tests, applicable typecheck or lint, and self-review of the diff |
| Medium | Targeted tests, relevant integration tests, final build, and one focused independent review |
| High | Full contract tests, real E2E, security/authorization/data-integrity checks, and independent correctness plus architecture review |

Apply checks to the actual changed inputs. For a documentation-only change, use existing documentation/contract validation and diff review; do not invent a browser matrix, runtime build, or low-value test. Documentation that changes executable instructions, public contracts, or generated build inputs may require broader verification. Reuse existing runners and meaningful tests before adding infrastructure.

Escalate the tier when evidence shows the original choice was wrong; record the reason. Do not apply the High tier to every task. If the user explicitly invokes another review workflow, its stricter verification contract takes precedence.

## Independent review

For Medium or High risk, or an explicitly required independent review, read [independent-review.md](independent-review.md) before constructing the review packet or assigning a reviewer. Low-risk self-review does not require that reference.

## Dirty worktree discipline

Record the initial status and a content fingerprint over `HEAD`, staged and unstaged diff bytes, and a canonical serialization of untracked path names, file types, executable mode bits, symlink targets, and content hashes. Separate pre-existing changes from workflow changes and avoid touching unrelated files. Review the final diff against that baseline before completion.

## Commit and handoff discipline

Skill activation does not authorize goal creation, a mode switch, a new thread, commit, push, PR, deployment, HANDOFF, or project-history updates. Preserve authority already granted; do not ask again. When the user authorizes commits, prefer stable boundaries:

1. product or runtime implementation;
2. tests and contracts; and
3. deployment and documentation.

Combine consecutive corrections with the same cause. Do not commit each small review hardening separately. Keep intermediate notes concise in the existing ledger and consolidate into authorized owning documentation at stable points. Only after a separate user request, refresh HANDOFF or project history at a stable checkpoint, before transfer, or at final completion. Timing guidance is not update authorization.

## Completion evidence

Completion requires satisfied acceptance criteria, required verification, zero current-scope blockers, understood worktree state, and recorded deferred observations. Optional optimization, unused deployment improvements, future operational automation, non-blocking architecture watch items, and unapproved expansion do not block completion.

Report implementation and verification separately: `implementation complete`, `integration verification in progress`, or `awaiting real-device verification`. Integration coverage of an earlier phase is verification of that feature, not reimplementation of the entire phase. Use the ledger to report changed state rather than repeatedly auditing every completed phase.

An unavailable required browser, device, independent-review capability, or other environment remains missing evidence, never a pass. Report the missing gate and minimum next action; do not waive it because of cost. A gap is accepted only through an explicit user-approved contract revision. Local completion and pre-publication real-device verification may be separate only when the approved contract defines that split. Otherwise the overall task remains incomplete even when the implementation is done.
