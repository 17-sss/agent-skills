# Agent Skills

English | [한국어](README.ko.md)

A catalog of small, independent workflows for repeated use across AI coding agents. It contains both agent-neutral skills built on common tools and Codex-native workflows that directly use Codex Plan, Goal, Review, and subagent capabilities.

![Agent Skills](assets/skill-visuals/agent-skills-dino-hero.png)

> Every skill is designed for standalone installation. Actions that change the user environment or external state—such as posting comments, pushing branches, opening pull requests, or installing a browser—remain subject to each skill's approval rules.

## Quick Start

Open the interactive catalog and choose the skills to install.

```bash
npx skills add https://github.com/17-sss/agent-skills
```

The selection screen is divided into two runtime-compatibility groups.

- `Codex`: explicitly invoked workflows that use native Codex Plan, Goal, Review, and subagent contracts
- `Other`: shared skills that work with Codex and other compatible agents

The `skills` CLI currently reads the explicit skill lists in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) as TUI grouping metadata. The group changes only how skills are presented; it does not select an install directory or add a Claude Code runtime dependency. See [Skill classification and installation](docs/skill-classification.md) for the audited dependency matrix.

Choose the target agent independently with `--agent`. For Codex, the current CLI installs project skills under `.agents/skills/` and global skills under `~/.codex/skills/`:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill reviewed-plan --agent codex
npx skills add https://github.com/17-sss/agent-skills --skill reviewed-plan --agent codex --global
```

You can also install a single skill.

```bash
npx skills add https://github.com/17-sss/agent-skills --skill <skill-name>
```

For example, install only `design-loop` with:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill design-loop
```

Start a new agent task after installation so the refreshed skill discovery result is loaded reliably. The executable contract for each skill lives in `skills/<skill-name>/SKILL.md`.

## At a Glance

| Category | Skill | Use it when |
| --- | --- | --- |
| Shared | [`design-loop`](skills/design-loop/SKILL.md) | Iteratively improving a UI against real rendered evidence |
| Shared | [`spec-interview`](skills/spec-interview/SKILL.md) | Resolving ambiguous requirements one material question at a time |
| Shared | [`visual-match`](skills/visual-match/SKILL.md) | Matching an implementation to an approved image or URL |
| Shared | [`handoff-memory`](skills/handoff-memory/SKILL.md) | Creating or resuming a repository or workspace HANDOFF |
| Shared | [`github-pr-review`](skills/github-pr-review/SKILL.md) | Reviewing a PR with `gh` and GitHub APIs and optionally posting the review |
| Shared | [`github-pr-publish`](skills/github-pr-publish/SKILL.md) | Safely pushing the current branch and publishing a pull request |
| Shared | [`commit-helper`](skills/commit-helper/SKILL.md) | Creating a commit that matches repository rules and staged changes |
| Codex-native | [`reviewed-plan`](skills/reviewed-plan/SKILL.md) | Producing an implementation plan reviewed by Planner, Architect, and Critic |
| Codex-native | [`completion-loop`](skills/completion-loop/SKILL.md) | Driving a clear Goal to evidence-backed completion |
| Codex-native | [`milestone-runner`](skills/milestone-runner/SKILL.md) | Executing large work as resumable, sequential milestones |
| Codex-native | [`review-gate`](skills/review-gate/SKILL.md) | Reviewing changes from two independent perspectives without modifying them |

## Shared Skills

These workflows do not depend on commands exclusive to one agent. They work in Codex and adapt to the browser, shell, GitHub, and image tools available in other compatible agents.

### design-loop

Refine UI implementation through an `inspect → implement → render → review → interact → fix → verify` loop. Validate desktop and mobile layouts, primary interactions, and visual regressions against real rendered output.

- Inspect existing design docs, tokens, components, and repository commands first.
- If no browser or screenshot capability exists, offer an isolated Chromium fallback only after user approval.
- Never claim visual completion or interaction success without rendered evidence.

Usage example:

```text
Use $design-loop to polish the checkout screen. Preserve behavior, inspect desktop and mobile renders, test the primary flow, and iterate on major visual issues.
```

### spec-interview

Inspect repository facts before implementation, ask one highest-leverage user decision at a time, and produce an execution-ready requirements specification.

- Keep the interview and repository inspection non-mutating.
- Do not ask the user for facts that tools can establish.
- Present bounded decisions with the agent's native choice control when available; otherwise show the same 2 or 3 options as a numbered list with a custom-answer escape hatch.
- Keep genuinely open-ended questions free-form instead of inventing choices.
- Finish when scope, non-goals, constraints, and testable completion criteria are clear.
- After readiness passes, optionally recommend only a best-fit workflow advertised in the current task; never require, install, or invoke it.

Usage example:

```text
Use $spec-interview to clarify organization-level API keys for this app. Inspect the existing model first, ask one material decision at a time, and do not implement anything yet.
```

### visual-match

Match an implementation to an approved screenshot, generated image, or live URL by repeatedly capturing the same viewport and UI state.

- Use semantic visual review first and pixel diff only as supporting localization evidence.
- Report an anchored `visual_similarity_percent` for every accepted viewport and state; use the lowest score and require `90+` with no blocking or major difference.
- Treat live references as read-only unless separately authorized to change external state.
- If no renderer exists, offer the approved isolated Chromium fallback; return `BLOCKED` before editing if rendering remains unavailable.

Usage example:

```text
Use $visual-match to match the attached checkout screenshot at desktop and mobile viewports, preserve the purchase flow, report the lowest visual similarity score, and explain every remaining difference.
```

### handoff-memory

Create, validate, refresh, and resume shared HANDOFF documents for one repository, a multi-repository workspace, or an individual workstream.

- Default to `docs/HANDOFF.md` for a repository and `_memory/HANDOFF.md` for a workspace.
- Preserve completed state as timestamped snapshots when useful.
- Keep mutable project memory in Git-trackable project locations instead of agent-specific configuration folders.

Usage example:

```text
Use $handoff-memory to refresh the canonical handoff for this repository, preserve the completed milestone as a snapshot, and validate the final document.
```

### github-pr-review

Review public or private pull requests with `gh`, local Git, tests, and GitHub APIs, then optionally post the review as the authenticated user.

- Accept a PR URL, `owner/repo#123`, a PR number, or the PR associated with the current branch.
- Verify account and repository access without printing authentication tokens.
- Draft findings first by default; publish only when explicitly requested or approved.

Usage example:

```text
Use $github-pr-review to review https://github.com/owner/repo/pull/123. Draft the findings first and do not post the review until I approve it.
```

### github-pr-publish

Preflight the local branch, perform the required push, and create a GitHub pull request in a safe sequence.

- Preview by default; do not push or create a PR without explicit approval.
- Distinguish private repository, organization SSO, permission, and remote mismatch failures.
- Block unsafe forks, force pushes, detached HEAD state, and incorrect remotes.

Usage example:

```text
Use $github-pr-publish to preflight the current branch and prepare a draft PR. Show the planned push and PR content before publishing anything.
```

### commit-helper

Inspect explicit repository rules, recent commit history, and staged changes to write a commit title and body that match the repository.

- Apply `explicit repository rules → recent history → conservative fallback` in that order.
- Infer meaning and scope from staged changes only.
- When the user asks for a commit, complete the local commit through the safe argv-based helper.

Usage example:

```text
Use $commit-helper to inspect this repository's commit rules and staged changes, then create the local commit. Do not push.
```

## Codex-native Workflows

The following four skills require Codex Goal, isolated Codex execution, native review, or subagent contracts to satisfy their completion gates. They are explicit-only and do not require any other catalog skill.

### reviewed-plan

Create an evidence-grounded implementation plan and pass it through independent Planner, Architect, and Critic gates in sequence.

- Do not edit files or install packages during planning.
- Run Critic review only after Architect approval.
- Include target files, symbols, risks, alternatives, and verification commands in the final handoff.
- After same-revision approval, optionally recommend only an available execution workflow; never require, install, or invoke it.

Usage example:

```text
/plan $reviewed-plan Plan a backward-compatible migration from local session state to server-managed sessions. Keep the workspace read-only and return the reviewed implementation handoff.
```

### completion-loop

Complete a clearly scoped Codex Goal through investigation, implementation, verification, failure diagnosis, and repair.

- Map every requirement to an implementation artifact and fresh evidence.
- Diagnose and fix failed verification instead of repeating it blindly.
- Require a separate read-only Codex review of the final implementation candidate.

Usage example:

```text
/goal Fix the reproducible cache invalidation regression, preserve public behavior, pass the existing tests and typecheck, and review the final diff. Use $completion-loop.
```

### milestone-runner

Split a large outcome into sequential, independently verifiable milestones and store durable state with an evidence ledger under `.agent-workflows/`.

- Execute only one milestone at a time and reject stale revisions or out-of-order work.
- Resume safely by validating the repository plan and hash-chained ledger.
- Finish only after every milestone, final verification, independent review, and native Goal reconciliation succeeds.

Usage example:

```text
Use $milestone-runner to migrate the authentication flow in three ordered stages, checkpoint each stage with tests, and finish only after final verification and an independent review.
```

The full state-helper command contract is documented in the [Goal state CLI reference](skills/milestone-runner/references/goal-state-cli.md).

### review-gate

Review current changes, files, a commit, a branch, or an already-readable PR target through independent correctness and architecture lanes.

- Freeze staged, unstaged, and untracked changes into a sensitivity-screened snapshot while retaining a parent-only original-target fingerprint.
- Keep credential values out of reviewer packets and return `INCONCLUSIVE` when redaction removes material evidence.
- Run both lanes in tool-enforced read-only sandboxes.
- Return prioritized findings and one of `APPROVE`, `COMMENT`, `REQUEST_CHANGES`, or `INCONCLUSIVE`.

Usage example:

```text
Use $review-gate to review all current staged, unstaged, and untracked changes. Keep the worktree unchanged and return independent correctness and architecture verdicts.
```

## Usage Principles

- Installing one skill must be sufficient for its core workflow to run.
- Optional workflow handoffs are recommendations only. A skill may name only a downstream workflow advertised in the current task's available-skill inventory; when that inventory or the best-fit skill is unavailable, it makes no suggestion.
- Shared skills follow their own invocation policy; specify `$skill-name` for reproducible explicit invocation.
- The four Codex-dependent workflows, plus the high-control shared `spec-interview` and `visual-match` workflows, set `allow_implicit_invocation: false` and must be invoked explicitly.
- When an optional plugin or tool is unavailable, prefer repository-native tools and safe fallbacks.
- Invoking a skill does not grant approval for external publishing, pushes, environment installation, or destructive actions.

## Maintenance and Validation

The source snapshot, native capability mapping, update cadence, and forward-test process for the six managed workflow skills are documented in [workflow skill maintenance](docs/native-workflow-skills-maintenance.md).

The two maintenance scripts have distinct responsibilities.

- `skills/milestone-runner/scripts/goal_state.py`: manages durable repository state for `milestone-runner` only.
- `scripts/check-native-workflow-skills.py`: validates the structure, independence, metadata, native capability contracts, TUI grouping, and source drift of the six managed workflow packages.

### Workflow checker modes

| Command | Network | Purpose |
| --- | --- | --- |
| `python3 scripts/check-native-workflow-skills.py` | No | Validate packages, metadata, links, independence, state roots, and catalog grouping |
| `python3 scripts/check-native-workflow-skills.py --require-validator` | No | Require the official `skill-creator` validator and a Python environment with PyYAML |
| `python3 scripts/check-native-workflow-skills.py --check-upstream` | Yes | Compare recorded source commits and current upstream fingerprints |
| `python3 scripts/check-native-workflow-skills.py --check-codex-docs` | Yes | Verify recorded native capability evidence against the current Codex manual |

Full acceptance check:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/check-native-workflow-skills.py --check-upstream --check-codex-docs --require-validator
```

Automated validation cannot prove every runtime behavior. After changing a complex contract, also run the isolated forward-test matrix in the maintenance documentation.

## Repository Structure

```text
agent-skills/
├── .claude-plugin/
│   └── marketplace.json  # Codex/Other TUI grouping metadata for the skills CLI
├── skills/                # one independently installable skill per directory
├── scripts/               # maintenance checks for package contracts and source drift
├── tests/                 # package and workflow contract regression tests
├── docs/                  # native capability mapping and forward-test records
└── assets/                # images used by root documentation
```

Each skill package contains the following files as needed.

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Core executable contract for the agent |
| `agents/openai.yaml` | Codex UI display name, description, and default prompt |
| `metadata.json` | Catalog metadata and reference documents |
| `references/` | Detailed contracts and rubrics loaded only when needed |
| `scripts/` | Package-local helpers for repeated deterministic work |
| `README.md`, `AGENTS.md` | Retained only when an existing package genuinely needs separate documentation or editing guidance |

When adding a skill or changing an existing contract, update `SKILL.md`, metadata, the root catalog, both language versions of the README, and related tests together. Run the validator after every structural change.
