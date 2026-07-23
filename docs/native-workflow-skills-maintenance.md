# Managed workflow skill maintenance

This repository maintains six namespaced, portable workflow skills:

- `spec-interview`
- `reviewed-plan`
- `completion-loop`
- `milestone-runner`
- `visual-match`
- `review-gate`

`reviewed-plan`, `completion-loop`, `milestone-runner`, and `review-gate` are Codex-dependent. `spec-interview` and `visual-match` are cross-agent workflows because their core contracts complete without a Codex-exclusive command. The authoritative classification and install-path rules are in [skill-classification.md](skill-classification.md).

The skills preserve user-facing workflow and quality gates without requiring an external orchestration runtime. Each package installs independently. Optional workflow handoffs are availability-gated recommendations, not runtime dependencies: they use only the current task's advertised skill inventory and never inspect, install, or invoke another package. Only `milestone-runner` needs durable workflow state, stored in the target repository under `.agent-workflows/`; the other five packages do not create a state directory.

## Native mapping

| Previous responsibility | Managed replacement |
| --- | --- |
| Structured interview prompt | Plan mode structured input, with one plain-text question as fallback |
| Stored interview state | Current task context; write a durable specification only when the user requests one |
| Workflow chaining | Readiness-gated, user-selected recommendations limited to downstream skills advertised in the current task |
| Consensus role routing | Native reviewers with explicit Planner, Architect, and Critic contracts plus enforced read-only sandboxing |
| Persistent completion loop | Goal mode plus a requirement-to-evidence completion audit |
| Durable multi-goal execution | One native aggregate goal plus ordered `.agent-workflows/goals/<slug>/` plan and ledger artifacts |
| Automatic retry hooks | Explicit investigate, implement, verify, diagnose, and repair loop |
| External architecture cross-check | Fresh native Codex reviewer running in an enforced read-only sandbox over captured requirements, diff, and logs |
| Live URL or image implementation | Product Design skills when installed, otherwise Browser, repository-native automation, or an approved isolated Chromium fallback |
| Visual verdict score | Fixed-weight anchored semantic score; optional pixel similarity remains separate secondary evidence |
| Diff or commit review target selection | Native `/review` target picker or equivalent read-only Git inspection |
| Code and architecture review roles | Two parallel native review lanes with enforced read-only isolation and independent evidence contracts |
| Merge recommendation synthesis | Deterministic `APPROVE`, `COMMENT`, `REQUEST_CHANGES`, or `INCONCLUSIVE` precedence |
| Resume and cleanup | Native Goal state plus revisioned repository-local artifacts only when durable multi-goal state is required |

## Reviewed sources

The initial rewrite was reviewed on 2026-07-20 against:

- [official upstream repository](https://github.com/Yeachan-Heo/oh-my-codex)
- upstream `main` commit `435d4a9cc982ffaf83fabbfbb8711ae6c178ffca`
- [Codex manual](https://developers.openai.com/codex/codex-manual.md)
- current Codex surfaces for Plan mode, Goal mode, `/review`, subagents, skills, plugins, Browser, image input, and image generation

Exact source fingerprints live in [native-workflow-sources.json](native-workflow-sources.json). The checker searches the current upstream skill archive by content, so legacy source filenames do not become local package identities. The hashes are drift detectors, not vendored copies and not a reason to reintroduce runtime-specific behavior.

## Suggested cadence

- Every two weeks, run the complete acceptance command to catch upstream and Codex documentation drift.
- Run it immediately after a meaningful Codex release or a change to Goal mode, `/review`, subagents, skills, plugins, Browser, Chrome, Product Design, image input, or image generation.
- Run the isolated forward-test matrix whenever a workflow contract changes. If no relevant behavior changed, run it at least quarterly as an end-to-end confidence check.
- A source hash or manual fragment change opens a review; it does not by itself justify copying upstream implementation details into a native package.

## Periodic update procedure

Run this after a meaningful Codex release, an upstream workflow change, or a Product Design, Browser, Chrome, image-generation, Goal, `/review`, or subagent interface change.

1. Check local contracts and upstream drift:

   ```bash
   python3 scripts/check-native-workflow-skills.py --check-upstream --check-codex-docs --require-validator
   ```

2. Refresh the current Codex manual. When the system `openai-docs` skill is available, prefer its manual helper:

   ```bash
   node "${CODEX_HOME:-$HOME/.codex}/skills/.system/openai-docs/scripts/fetch-codex-manual.mjs"
   ```

   Otherwise read the official manual URL recorded in the source manifest.

3. Re-check these product contracts:

   - `/plan` still provides a planning boundary and structured questions for Codex-dependent planning workflows
   - `/goal` still provides persisted goals and automatic continuation
   - `/review` still supports base-branch, uncommitted, commit, and custom-instruction targets without modifying the worktree
   - goal creation, completion, and blocked-state rules have not changed
   - Goal mode still preserves the current permission boundary rather than granting broader access
   - native subagent creation, permission inheritance, custom-agent sandbox overrides, context isolation, steering, and completion semantics have not changed
   - Browser availability across App, CLI, and IDE remains accurate
   - Chrome remains the correct route for the user's existing browser profile
   - a missing renderer triggers an approval-gated, repository-isolated Chromium offer before `BLOCKED`
   - Product Design skill names and invocation syntax remain available
   - image generation still requires approval before a generated reference becomes implementation truth
   - `SKILL.md` and `agents/openai.yaml` schema requirements remain current

4. Compare changed upstream text by behavior category:

   - preserve user-visible intent, gates, review order, and evidence requirements
   - discard unrelated runtime state, compatibility code, terminal coordination, hidden retry, and plugin-specific shims
   - preserve only explicit durable goal artifacts under `.agent-workflows/` when the workflow genuinely needs restartable state
   - map genuinely new behavior to the smallest documented Codex capability
   - keep every skill installable independently
   - keep optional handoffs recommendation-only and allowlisted; never infer installed skills from the filesystem or catalog

5. Update only the affected `SKILL.md`, scripts, referenced contract, `agents/openai.yaml`, `metadata.json`, root catalog entry, source fingerprint, and checker inventory. If the minimum runtime changes, also update `CODEX_SKILL_NAMES`, `OTHER_SKILL_NAMES`, [skill-classification.md](skill-classification.md), and TUI grouping tests.

6. Run structural validation, banned-dependency checks, official Codex-manual evidence checks, and the isolated forward-test matrix. Inspect the final diff after all validators run.

The automated acceptance command is:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/check-native-workflow-skills.py --check-upstream --check-codex-docs --require-validator
```

### Checker CLI contract

The default invocation is offline. It checks frontmatter, package-local links, executable helper bits, metadata and `agents/openai.yaml`, banned runtime dependencies, hard cross-skill dependencies, the strict optional-handoff allowlist and availability guardrails, the exclusive `.agent-workflows/` state owner, the root catalog, and retired unprefixed directories. It also runs `skill-creator`'s `quick_validate.py` when that validator and a Python interpreter with PyYAML are available.

Use the flags according to the evidence required:

| Flag | Effect |
| --- | --- |
| `--require-validator` | Treat a missing `quick_validate.py`, missing PyYAML-capable interpreter, or validator failure as an acceptance failure |
| `--check-upstream` | Use `git ls-remote` and current raw source files to compare the recorded upstream commit and hashes |
| `--check-codex-docs` | Fetch the current official Codex manual and verify every capability fragment in the manifest |
| `--validator <path>` | Override `SKILL_VALIDATOR` and the current Codex system-skill location |
| `--validator-python <path>` | Override `SKILL_VALIDATOR_PYTHON` and automatic interpreter discovery |

The network flags are opt-in and may be combined. The checker returns `0` only when every requested check passes and `1` after any validation error. Without `--require-validator`, dependency-free repository checks may still pass while an unavailable validator is explicitly reported as skipped. The checker never installs packages or writes workflow state.

The validator location in the current Codex system skill is only a convenience default. Interpreter discovery tries the current Python, then `python3` and `python` from `PATH`, then `/usr/bin/python3`, and accepts the first candidate that imports PyYAML.

Manual-fragment validation is a drift canary, not semantic proof. Permission inheritance, Goal access boundaries, Browser surface availability, and `/review` target behavior must also be confirmed in the behavioral forward tests or by a human reading the refreshed official section.

Do not call the packages release-ready from the automated command alone. Run the forward-test prompts below in disposable Git fixtures, record the agent trace and before/after content fingerprints, and require every row in the behavioral matrix to pass.

## Skill-specific audit

### spec-interview

- Still inspect repository facts before asking the user.
- Still ask one high-leverage question per round.
- Keep non-goals, decision boundaries, and testable completion criteria as mandatory readiness gates.
- Do not restore numeric ambiguity scores or artificial interview length.
- When repository inspection is delegated, verify exact content fingerprints before trusting the read-only result.
- Skip optional delegation unless the delegated worker has a tool-enforced read-only boundary; prompt wording is not a safety boundary.
- Include file type, executable bits, symlink target, and content in path fingerprints; names and bytes alone miss identity-only changes.
- Offer a downstream workflow only after the readiness gate passes, only when its exact name appears in the current task's available-skill inventory, only when the current agent satisfies its advertised runtime requirements, and only as a user-selected recommendation.
- When the inventory is absent, the best-fit route is unavailable, or material ambiguity remains, omit the optional handoff instead of searching installation paths or substituting an unsafe route.

### reviewed-plan

- Keep the workspace read-only.
- Preserve Planner, then Architect, then Critic ordering.
- Ensure non-approval repeats the complete review sequence.
- Never report consensus without matching Architect and Critic approval.
- Compare exact staged, unstaged, and untracked content across every delegated gate; `git status` text alone is insufficient.
- Require an inherited or isolated effective read-only sandbox for Architect and Critic; otherwise return `NOT APPROVED`.
- Keep Architect and Critic terminal review lanes; they must not reactivate workflows or delegate recursively.
- Offer an execution workflow only after matching Architect `ACCEPT` and Critic `APPROVE`, only when its exact name appears in the current task's available-skill inventory, and only as a user-selected recommendation.
- When approval, readiness, inventory, or the best-fit route is unavailable, omit the optional handoff instead of searching installation paths or substituting an unsafe route.

### completion-loop

- Verify goal-tool rules before changing completion or blocked behavior.
- Preserve the requirement-to-artifact-to-evidence audit.
- Keep reviewer input free from the leader's verdict or suspected answer.
- Do not turn persistence into expanded destructive or production authority.
- Invalidate and repeat independent review whenever implementation artifacts change after review.
- Because implementation turns are writable, run completion review through a separate native Codex execution explicitly sandboxed read-only; otherwise do not complete the goal.
- Keep the completion reviewer terminal and include filesystem identity as well as content in the candidate fingerprint.

### milestone-runner

- Keep the package standalone; never make another catalog skill a required or implicit dependency.
- Keep mutable state under `.agent-workflows/goals/<slug>/` and never under `.codex/` or an installed skill directory.
- Keep the operator-facing command, output, exit, recovery, and troubleshooting contract aligned with [goal-state-cli.md](../skills/milestone-runner/references/goal-state-cli.md).
- Preserve one native aggregate goal while repository artifacts track ordered subgoals; do not emulate multiple simultaneous native goals.
- Keep the parent task as the single state owner. Delegated work returns evidence but never mutates the plan or ledger.
- Require the current revision for every mutation and verify the ledger hash chain before trusting resume state.
- Never overwrite an existing plan, skip an earlier blocked goal, delete superseded history, or weaken accepted verification through steering.
- Keep the state helper limited to repository artifacts. Native `get_goal`, `create_goal`, and `update_goal` remain model-facing tool calls.
- Finalize only after all subgoals are terminal, requirements are proved, verification passes, implementation changes receive an independent read-only review, and a fresh native goal snapshot is complete.

### visual-match

- Re-check Product Design, Browser, Chrome, Playwright, image-input, and image-generation routing.
- Preserve the missing-renderer sequence: inspect existing capabilities, offer isolated Chromium with explicit approval, smoke-test it, then return `BLOCKED` if declined or unusable.
- Keep the bootstrap outside the target repository. Never mutate manifests, lockfiles, `node_modules`, branded browsers, system packages, or another skill as part of the fallback.
- Preserve approval before implementing a generated reference.
- Compare equivalent route, data, viewport, and UI states.
- Preserve the fixed scoring weights, anchored levels, N/A normalization, lowest-target aggregation, and default `90` threshold in `score_visual_match.py` and `comparison-rubric.md`.
- Keep `visual_similarity_percent` semantic and scope-bound. Never blend optional pixel similarity into it or let a score override blocking or major differences.
- Keep the scorer Python-standard-library-only, package-local, state-free, and independently executable without another skill or dependency installation.
- Preflight capture capability before editing and return `BLOCKED` or `INCOMPLETE` when a blocking or major mismatch remains unresolved.
- Keep live-reference interaction non-mutating by default and require separate explicit authority for state changes.

### review-gate

- Re-check native `/review` target semantics before changing scope resolution.
- Keep current changes inclusive of staged, unstaged, and untracked files.
- Preserve two independent, tool-enforced read-only lanes and never approve when either lane is unavailable or evidence-free.
- Use target-specific snapshots for current changes, commits, branch ranges, and file audits. Give each lane identical captured content with its own non-writable packet and return `INCONCLUSIVE` if any digest or applicable worktree baseline drifts.
- Keep file audits usable outside Git, and run any confirming checks only in a no-write or disposable environment with caches redirected.
- Recompute the complete live content-and-filesystem-identity fingerprint after both lanes; `git status` is context, not a mutation detector.
- Keep each review lane terminal so the two-lane workflow cannot recursively invoke itself.
- Keep priority separate from the merge-blocking flag and retain architecture `WATCH` or `BLOCK` concerns visibly.
- Do not restore runtime phase state, external advisor shims, universal complexity thresholds, or automatic fixes.
- Keep change-review attribution separate from full-content file-audit findings.

## Forward-test prompts

Run tests in disposable or read-only fixtures. Do not let validation agents edit a live project or external system.

```text
Use $spec-interview to clarify organization-level API keys for this existing app. I have not decided ownership, migration, or revocation behavior.
```

```text
/plan Use $reviewed-plan. Plan a backward-compatible migration from local session state to server-managed sessions in this repository. Do not edit files.
```

```text
/goal Fix a reproducible cache invalidation regression and prove it with the existing tests, typecheck, and final diff review. Use $completion-loop.
```

```text
Use $milestone-runner to migrate this disposable two-module fixture in two ordered stages, checkpoint each stage, and finish only after tests and an independent review pass.
```

```text
Use $visual-match to match the supplied checkout screenshot at desktop and mobile viewports, preserve behavior, report the lowest anchored visual similarity score, and explain every remaining difference.
```

```text
Use $review-gate to review all current staged, unstaged, and untracked changes. Keep the worktree unchanged and return independent correctness and architecture verdicts.
```

For every forward test, verify the trace as well as the final prose: question count, repository writes, review ordering, failure diagnosis, fresh evidence, screenshot state equivalence, and honest blockers matter more than fluent output.

### Behavioral pass matrix

| Skill | Required observable behavior | Integrity assertion |
| --- | --- | --- |
| `spec-interview` | Inspects repository evidence, asks exactly one material user decision, and waits | Fixture fingerprint remains unchanged |
| `reviewed-plan` | Produces a repository-grounded plan, runs Architect before Critic, and reports both verdicts | Fixture fingerprint remains unchanged across both gates |
| `completion-loop` | Reproduces the failure, implements the smallest fix, runs fresh checks, and independently reviews the final fingerprint | Only the disposable fixture changes and its tests pass |
| `milestone-runner` | Creates `.agent-workflows/`, runs goals sequentially, rejects stale or out-of-order transitions, checkpoints evidence, and reconciles a completed native goal | Only the disposable fixture and its explicit durable state change; no other skill is invoked |
| `visual-match` | With installation prohibited, offers the isolated Chromium fallback but performs no download and returns the safe missing-browser blocker; with a browser already available, completes baseline/edit/recapture, scores every equivalent target, uses the lowest score, and never passes below threshold or with unresolved major drift | Only the disposable fixture and task-scoped captures change; the package-local scorer creates no state |
| `review-gate` | Includes staged, unstaged, and untracked content, runs both lanes, and catches seeded actionable defects | The complete fixture fingerprint remains unchanged |

Keep forward-test fixtures outside the repository. Do not install dependencies, touch user configuration, contact production systems, post external reviews, or leave browser sessions and temporary artifacts running. Record current results in [native-workflow-forward-test-report.md](native-workflow-forward-test-report.md).

## Installation

The six managed packages use short functional identifiers and remain explicit-only and independently installable. Only the four Codex-dependent packages use `Codex · …` OpenAI display names. Choose the target agent independently from the TUI classification:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill spec-interview
npx skills add https://github.com/17-sss/agent-skills --skill reviewed-plan
npx skills add https://github.com/17-sss/agent-skills --skill completion-loop
npx skills add https://github.com/17-sss/agent-skills --skill milestone-runner
npx skills add https://github.com/17-sss/agent-skills --skill visual-match
npx skills add https://github.com/17-sss/agent-skills --skill review-gate
```

For Codex, project installs intentionally use `.agents/skills/`; global installs use `~/.codex/skills/`. See [skill-classification.md](skill-classification.md) for the audited matrix and commands. Start a new agent task after installation so skill discovery does not retain stale definitions.

## Known native differences

- Without Goal mode, Codex Completion Loop can preserve the completion contract only inside the current task; it cannot promise cross-task automatic continuation.
- Without Goal mode, Codex Milestone Runner can preserve repository-local plan and ledger artifacts but cannot promise automatic continuation. It also cannot clear or replace a conflicting active native goal. After a native goal is completed, `get_goal` may report no active goal, so preserve the successful `update_goal` completion result before querying again.
- Plan mode is a semantic boundary, not a separate filesystem sandbox. Codex Reviewed Plan requires an effective read-only permission mode for independent gates and uses content fingerprints only as defense in depth.
- Native subagents inherit the parent permission mode. A writable implementation turn therefore cannot claim an isolated review merely by prompting the child to stay read-only; Codex Completion Loop uses a separately sandboxed native Codex run or remains incomplete.
- Browser, image, and design capabilities vary by agent surface and installed plugins. Visual Match falls back to repository-native automation, then offers a user-approved isolated Chromium renderer before reporting missing visual evidence.
- Native `/review` is sufficient for an ordinary isolated review. Codex Review Gate deliberately spends more tokens on two independent lanes and returns `INCONCLUSIVE` if that evidence cannot be collected.
- Generated-image approval naturally spans turns because image generation can end the generation turn.
