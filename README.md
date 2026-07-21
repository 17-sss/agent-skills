# Agent Skills

A collection of reusable skills for AI coding agents. Skills are packaged instructions and helper scripts that extend agent capabilities while keeping the workflow repository-friendly.

![Agent Skills](assets/skill-visuals/agent-skills-dino-hero.png)

## Available Skills

### design-loop

Agent-neutral workflow for building and refining interfaces through rendered screenshots, interaction testing, responsive checks, and bounded visual iteration.

**Use when:**
- Building or polishing UI, frontend, product, dashboard, admin, landing-page, or game screens
- Inspecting the same implementation at desktop and mobile viewports
- Testing visible user flows and interaction states before declaring the design complete
- Comparing a small number of visual alternatives with a consistent rubric
- Integrating a generated raster asset and validating it inside the real interface

**Behavior:**
- Inspects existing design docs, components, tokens, routes, and repository commands first
- Captures a baseline and requires fresh rendered evidence for visual-quality claims
- Reviews hierarchy, spacing, typography, contrast, responsiveness, interaction states, and runtime quality
- Adapts to available app, CLI, or IDE capabilities without requiring one browser or MCP integration
- Offers a user-approved, repository-isolated Chromium fallback only when no existing renderer can provide evidence
- Uses image generation selectively and keeps variant exploration bounded

### spec-interview

Codex-native requirements interview for turning an ambiguous idea into an execution-ready specification before planning or implementation.

**Use when:**
- Invoking `/plan $spec-interview` for a broad idea or underspecified change
- Asking Codex to interview you, challenge assumptions, or avoid guessing
- Clarifying scope, non-goals, constraints, decision boundaries, or acceptance criteria

**Behavior:**
- Investigates repository facts before asking the user
- Asks one highest-leverage question at a time
- Pressure-tests only material assumptions and boundary cases
- Stops when another answer would no longer change implementation or verification
- Produces a testable requirements specification without modifying project files
- Delegates repository mapping only through a tool-enforced read-only Codex sandbox

### reviewed-plan

Read-only consensus planning through sequential Planner, Architect, and Critic review.

**Use when:**
- Invoking `/plan $reviewed-plan` for architecture-heavy or high-risk work
- Requiring a reviewed plan before implementation
- Needing concrete files, symbols, alternatives, risks, and verification commands in a handoff

**Behavior:**
- Grounds the plan in repository and authoritative external evidence
- Requires an effective read-only sandbox for independent reviewers and records a content baseline as defense in depth
- Runs Architect only after the Planner draft, then Critic only after Architect acceptance
- Repeats the complete review sequence for non-approval
- Stops after an approved or explicitly not-approved implementation handoff

### completion-loop

Verified-completion workflow that pairs Codex Goal mode with an evidence-driven implementation and repair loop.

**Use when:**
- Invoking `/goal ... Use $completion-loop`
- Asking Codex to finish, keep going, or not stop before verified completion
- Requiring tests, final diff review, and requirement-by-requirement evidence

**Behavior:**
- Binds work to an explicit outcome, constraints, acceptance criteria, and proof methods
- Learns from test failures instead of repeating blind retries
- Uses a fresh, separately sandboxed read-only Codex reviewer for every final implementation candidate
- Audits every requirement against implementation artifacts and fresh evidence
- Reports genuine blockers without treating ordinary difficulty as blocked work

### milestone-runner

Standalone durable multi-goal execution over native Codex Goal mode and repository-local checkpoints.

**Use when:**
- Invoking `$milestone-runner` for a large outcome that should survive task restarts
- Breaking implementation into ordered, independently verifiable goals
- Requiring evidence checkpoints, safe resume, explicit plan steering, and final goal reconciliation

**Behavior:**
- Creates only the required plan state under `.agent-workflows/goals/<slug>/` in the target repository
- Executes one non-terminal goal at a time and rejects stale revision writes
- Uses a hash-chained ledger without calling Codex goal tools from shell scripts
- Blocks later work behind unresolved earlier goals and preserves superseded history
- Requires fresh verification, an independent native read-only review for implementation changes, and a completed native goal snapshot before finalization
- Installs and runs without any other catalog skill
- Documents the bundled state helper's commands, revision discipline, recovery behavior, and failure handling in the [Goal state CLI reference](skills/milestone-runner/references/goal-state-cli.md)

### visual-match

Strict visual-reference implementation loop for approved images, generated mockups, and live-URL baselines.

**Use when:**
- Invoking `/goal ... Use $visual-match`
- Matching a screenshot or live URL at defined viewports and states
- Making visual fidelity and reusable design-system decisions part of completion

**Behavior:**
- Routes across Product Design, Browser, Chrome, image, or repository-native automation based on availability
- Requires user approval before implementing a generated reference
- Captures and compares equivalent routes, data, viewports, and UI states
- Uses pixel diff only as secondary evidence and avoids arbitrary visual scores
- Offers a user-approved, repository-isolated Chromium fallback before stopping when equivalent capture is unavailable
- Never modifies project dependencies or installs system packages as part of that fallback
- Keeps live-reference interactions non-mutating unless the user separately authorizes an exact external action
- Verifies interactions, responsive behavior, code checks, and remaining visual differences

### review-gate

Read-only comprehensive code review built on Codex-native review targeting and sandbox-isolated review lanes.

**Use when:**
- Invoking `$review-gate` for current changes, files, a commit, branch, checked-out PR-style target, or a PR already readable through configured GitHub tooling
- Requiring correctness and architecture perspectives before merge
- Needing prioritized file-and-line findings and a deterministic readiness verdict

**Behavior:**
- Reuses a target selected through native `/review` or captures the exact current-change, commit, branch-range, or explicit-file target
- Separates Git change attribution from full-content explicit-file audits
- Runs independent correctness and architecture lanes in parallel under tool-enforced read-only isolation
- Separates finding priority from merge-blocking impact
- Returns `APPROVE`, `COMMENT`, `REQUEST_CHANGES`, or `INCONCLUSIVE` through fixed precedence rules
- Does not edit, stage, commit, push, or post external review comments

### handoff-memory

Agent-neutral workflow for creating and maintaining shared repo-local, workspace-wide, or workstream-specific HANDOFF and memory documents.

**Use when:**
- Writing a project handoff before ending a session
- Writing a workspace handoff from a parent folder that coordinates multiple repos
- Resuming work from an existing handoff
- Standardizing shared project-state notes in Git-trackable files
- Keeping mutable handoff state out of `.codex`, `.claude`, `.windsurf`, or `.agents`

**Behavior:**
- Reuses an existing shared handoff file such as `docs/HANDOFF.md`, `memories/HANDOFF.md`, or `HANDOFF.md`
- Defaults to `docs/HANDOFF.md` for a repo and `_memory/HANDOFF.md` for a workspace
- Supports workstream-specific workspace documents under `_memory/workstreams/<name>/`
- Adds helper scripts for create, validate, and staleness checks
- Supports optional timestamped snapshots with explicit kind/reason metadata under `docs/handoffs/` or `_memory/handoffs/`
- Supports global or project-local skill installation, while keeping the shared data inside the repository or workspace root

### github-pr-review

Agent-neutral workflow for reviewing GitHub pull requests with `gh`, local `git`, tests, and GitHub APIs, then posting review comments as the authenticated GitHub account.

**Use when:**
- Setting up OAuth or GitHub CLI authentication for PR reviews
- Reviewing a PR URL, `owner/repo#123`, or the current branch PR
- Leaving review comments as the user's GitHub account
- Reviewing public or private repository PRs
- Collecting PR diff, checks, and related code context before drafting feedback

**Behavior:**
- Checks `gh auth status` and confirms the posting account without exposing tokens
- Supports PR URLs, `owner/repo#123`, PR numbers, branches, and current-branch PR lookup
- Separates public read access from authenticated review posting
- Explains private repo failures such as missing access, org SSO, or insufficient scopes
- Drafts findings first and posts only after confirmation unless immediate posting was requested
- Uses explicit-only `approve` and `request-changes` events

### github-pr-publish

Agent-neutral workflow for safely publishing GitHub pull requests with `gh`, local `git`, and constrained GitHub REST fallback.

**Use when:**
- Creating, opening, publishing, or preflighting a GitHub pull request from a local branch
- Publishing PRs for public or private repositories through the authenticated GitHub CLI account
- Pushing a local feature branch only as an explicit part of PR creation
- Diagnosing PR creation failures such as missing auth, org SSO, insufficient permission, private repo not-found masking, or validation errors
- Avoiding unsafe `gh pr create` prompting, fork creation, or accidental pushes

**Behavior:**
- Previews by default and performs no push, PR creation, browser open, or mutating API call without explicit confirmation flags
- Requires prompt-free PR content and an explicit `--head` for creation
- Guards pushes behind `--push --remote <name> --yes` and rejects unsafe branch, fork, force, detached HEAD, and wrong-remote cases
- Supports constrained REST fallback only after remote-head verification
- Includes fake `gh`/`git` tests for command construction, no-mutation defaults, and token redaction

### commit-helper

Reusable commit-message helper that inspects explicit repo-local rules, recent history, and staged changes before drafting or creating commits.

**Use when:**
- The user asks for a commit message
- The user wants to commit staged changes but the repo convention is unclear
- A workflow needs to create commits in the target repository's local style
- The current repository may use conventional, gitmoji, plain imperative, or custom commit formats

**Behavior:**
- Follows `explicit local rules > recent history > conservative fallback`
- Uses staged changes only when drafting commit messages
- Separates commit format from repo-local phrasing
- Falls back to Conventional Commits when no strong local signal exists
- Supports conventional, gitmoji, plain imperative, and repo-custom styles
- Uses a safe script path for multiline commit bodies without literal `\n`

## Installation

Install from this collection interactively:

```bash
npx skills add https://github.com/17-sss/agent-skills
```

The CLI will inspect the repository, show the available skills, and guide you through the install flow.

Install a specific skill directly:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill <skill-name>
```

Example:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill handoff-memory
```

## Usage

Once installed, agents can invoke the relevant skill when a task matches it. The executable contract lives in `skills/<skill-name>/SKILL.md`; established packages may also include a human-facing README.

The native workflow skills are designed for these Codex entry points:

```text
/plan $spec-interview <idea or task>
/plan $reviewed-plan <task to plan>
/goal <outcome and verification criteria>. Use $completion-loop.
Use $milestone-runner to complete <large outcome, constraints, and verification criteria> as a durable sequential plan.
/goal <visual target and verification criteria>. Use $visual-match.
Use $review-gate to review <files, commit, branch, checked-out PR-style target, or current changes>.
```

The six native workflow packages intentionally omit per-skill README and AGENTS files because those files would only duplicate `SKILL.md` or root guidance. Their executable contract lives in `SKILL.md`, with detailed review and verification contracts under `references/`. They set `allow_implicit_invocation: false` and remain independently installable: no package requires another catalog skill.

## Maintenance

See [Codex-native workflow skill maintenance](docs/native-workflow-skills-maintenance.md) for the upstream source snapshot, Codex capability mapping, periodic update checklist, validation command, forward-test prompts, and post-migration installation steps.

The two scripts added for the native workflow collection have separate responsibilities:

- `skills/milestone-runner/scripts/goal_state.py` owns only one installed skill's durable repository state. Its complete operator contract is in the [Goal state CLI reference](skills/milestone-runner/references/goal-state-cli.md).
- `scripts/check-native-workflow-skills.py` validates all six catalog packages. It does not edit packages, install dependencies, or create workflow state.

### Workflow checker modes

| Command | Network | Purpose |
| --- | --- | --- |
| `python3 scripts/check-native-workflow-skills.py` | No | Run dependency-free package, metadata, link, standalone, state-root, and catalog checks; also run `quick_validate.py` when available |
| `python3 scripts/check-native-workflow-skills.py --require-validator` | No | Require the official `skill-creator` validator and a Python interpreter with PyYAML |
| `python3 scripts/check-native-workflow-skills.py --check-upstream` | Yes | Compare the recorded source commit and file hashes with the current upstream ref |
| `python3 scripts/check-native-workflow-skills.py --check-codex-docs` | Yes | Check the current official Codex manual for every recorded native capability fragment |

Flags can be combined. Run the complete acceptance check with:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/check-native-workflow-skills.py --check-upstream --check-codex-docs --require-validator
```

The checker returns `0` only when every requested check passes and `1` when it records any validation error. It tries the current Python, then `python3` and `python` from `PATH`, then `/usr/bin/python3`, accepting the first interpreter that can import PyYAML. Override the validator with `--validator <path>` or `SKILL_VALIDATOR`, and its interpreter with `--validator-python <path>` or `SKILL_VALIDATOR_PYTHON`. Automated checks cover package contracts and current official documentation evidence; release confidence also requires the isolated forward-test matrix in the maintenance guide.

## Repository Structure

Each skill lives under `skills/<skill-name>/` and may contain:

- `SKILL.md` - Primary skill definition
- `README.md` - Human-facing documentation
- `AGENTS.md` - Agent-facing repo guidance for the skill package
- `metadata.json` - Catalog metadata
- `scripts/` - Helper scripts
- `references/` - Supporting docs and templates
- `agents/` - Optional agent-specific metadata such as `openai.yaml`
