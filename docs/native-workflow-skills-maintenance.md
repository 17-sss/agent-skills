# Codex-native workflow skill maintenance

This repository replaces five frequently used orchestration workflows with portable Codex skills:

- `spec-interview`
- `reviewed-plan`
- `completion-loop`
- `visual-match`
- `review-gate`

The new skills preserve the user-facing workflow and quality gates. They do not emulate the old runtime, state directory, terminal UI, hook loop, or MCP compatibility layers.

## Native mapping

| Previous responsibility | Codex-native replacement |
| --- | --- |
| Structured interview prompt | Plan mode structured input, with one plain-text question as fallback |
| Stored interview state | Current task context; write a durable specification only when the user requests one |
| Consensus role routing | Native reviewers with explicit Planner, Architect, and Critic contracts plus enforced read-only sandboxing |
| Persistent completion loop | Goal mode plus a requirement-to-evidence completion audit |
| Automatic retry hooks | Explicit investigate, implement, verify, diagnose, and repair loop |
| External architecture cross-check | Fresh native Codex reviewer running in an enforced read-only sandbox over captured requirements, diff, and logs |
| Live URL or image implementation | Product Design skills when installed, otherwise Browser or repository-native automation |
| Visual verdict score | Structured semantic comparison; pixel diff only as secondary evidence |
| Diff or commit review target selection | Native `/review` target picker or equivalent read-only Git inspection |
| Code and architecture review roles | Two parallel native review lanes with enforced read-only isolation and independent evidence contracts |
| Merge recommendation synthesis | Deterministic `APPROVE`, `COMMENT`, `REQUEST_CHANGES`, or `INCONCLUSIVE` precedence |
| Runtime resume and cleanup | Goal state when available and ordinary task completion semantics |

## Reviewed sources

The initial rewrite was reviewed on 2026-07-20 against:

- [official upstream repository](https://github.com/Yeachan-Heo/oh-my-codex)
- upstream `main` commit `435d4a9cc982ffaf83fabbfbb8711ae6c178ffca`
- [Codex manual](https://developers.openai.com/codex/codex-manual.md)
- current Codex surfaces for Plan mode, Goal mode, `/review`, subagents, skills, plugins, Browser, image input, and image generation

Exact source fingerprints live in [native-workflow-sources.json](native-workflow-sources.json). The checker searches the current upstream skill archive by content, so legacy source filenames do not become local package identities. The hashes are drift detectors, not vendored copies and not a reason to reintroduce runtime-specific behavior.

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

   - `/plan` still provides a planning boundary and structured questions
   - `/goal` still provides persisted goals and automatic continuation
   - `/review` still supports base-branch, uncommitted, commit, and custom-instruction targets without modifying the worktree
   - goal creation, completion, and blocked-state rules have not changed
   - Goal mode still preserves the current permission boundary rather than granting broader access
   - native subagent creation, permission inheritance, custom-agent sandbox overrides, context isolation, steering, and completion semantics have not changed
   - Browser availability across App, CLI, and IDE remains accurate
   - Chrome remains the correct route for the user's existing browser profile
   - Product Design skill names and invocation syntax remain available
   - image generation still requires approval before a generated reference becomes implementation truth
   - `SKILL.md` and `agents/openai.yaml` schema requirements remain current

4. Compare changed upstream text by behavior category:

   - preserve user-visible intent, gates, review order, and evidence requirements
   - discard runtime state, compatibility code, terminal coordination, hidden retry, and plugin-specific shims
   - map genuinely new behavior to the smallest documented Codex capability
   - keep every skill installable independently

5. Update only the affected `SKILL.md`, scripts, referenced contract, `agents/openai.yaml`, `metadata.json`, root catalog entry, source fingerprint, and `SKILL_NAMES` registry in the checker. Keep local names functional and let archive fingerprints detect upstream drift without preserving upstream filenames as package identities.

6. Run structural validation, banned-dependency checks, official Codex-manual evidence checks, and the isolated forward-test matrix. Inspect the final diff after all validators run.

The automated acceptance command is:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/check-native-workflow-skills.py --check-upstream --check-codex-docs --require-validator
```

It makes `skill-creator`'s `quick_validate.py` mandatory and verifies that the current official Codex manual still contains evidence for every capability recorded in the manifest. The system-skill location is only a convenience default: use `--validator <path>` or `SKILL_VALIDATOR` when the validator lives elsewhere. The checker tries the current Python, then `python3` and `python` from `PATH`, then the common `/usr/bin/python3` fallback, accepting only an interpreter that imports PyYAML. Use `--validator-python <path>` or `SKILL_VALIDATOR_PYTHON` to select another interpreter. Without `--require-validator`, dependency-free repository checks may still run, but a skipped validator is reported without claiming full validation. The checker never installs packages.

Manual-fragment validation is a drift canary, not semantic proof. Permission inheritance, Goal access boundaries, Browser surface availability, and `/review` target behavior must also be confirmed in the behavioral forward tests or by a human reading the refreshed official section.

Do not call the packages release-ready from the automated command alone. Run the forward-test prompts below in disposable Git fixtures, record the agent trace and before/after content fingerprints, and require every row in the behavioral matrix to pass.

## Skill-specific audit

### spec-interview

- Still inspect repository facts before asking the user.
- Still ask one high-leverage question per round.
- Keep non-goals, decision boundaries, and testable completion criteria as mandatory readiness gates.
- Do not restore numeric ambiguity scores or artificial interview length.
- When repository inspection is delegated, verify exact content fingerprints before trusting the read-only result.
- Skip optional delegation unless the child's effective sandbox is tool-enforced read-only; prompt wording is not a safety boundary.
- Include file type, executable bits, symlink target, and content in path fingerprints; names and bytes alone miss identity-only changes.

### reviewed-plan

- Keep the workspace read-only.
- Preserve Planner, then Architect, then Critic ordering.
- Ensure non-approval repeats the complete review sequence.
- Never report consensus without matching Architect and Critic approval.
- Compare exact staged, unstaged, and untracked content across every delegated gate; `git status` text alone is insufficient.
- Require an inherited or isolated effective read-only sandbox for Architect and Critic; otherwise return `NOT APPROVED`.
- Keep Architect and Critic terminal review lanes; they must not reactivate workflows or delegate recursively.

### completion-loop

- Verify goal-tool rules before changing completion or blocked behavior.
- Preserve the requirement-to-artifact-to-evidence audit.
- Keep reviewer input free from the leader's verdict or suspected answer.
- Do not turn persistence into expanded destructive or production authority.
- Invalidate and repeat independent review whenever implementation artifacts change after review.
- Because implementation turns are writable, run completion review through a separate native Codex execution explicitly sandboxed read-only; otherwise do not complete the goal.
- Keep the completion reviewer terminal and include filesystem identity as well as content in the candidate fingerprint.

### visual-match

- Re-check Product Design, Browser, Chrome, Playwright, image-input, and image-generation routing.
- Preserve approval before implementing a generated reference.
- Compare equivalent route, data, viewport, and UI states.
- Do not replace semantic review with an arbitrary visual score.
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
/plan Use $spec-interview. I want to add organization-level API keys to this existing app, but I have not decided ownership, migration, or revocation behavior.
```

```text
/plan Use $reviewed-plan. Plan a backward-compatible migration from local session state to server-managed sessions in this repository. Do not edit files.
```

```text
/goal Fix a reproducible cache invalidation regression and prove it with the existing tests, typecheck, and final diff review. Use $completion-loop.
```

```text
/goal Match the supplied checkout screenshot at desktop and mobile viewports, preserve behavior, and report every remaining visual difference. Use $visual-match.
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
| `visual-match` | Proves both the safe missing-browser blocker and a browser-enabled baseline/edit/recapture/comparison success path; never passes unresolved major drift | Only the disposable fixture and task-scoped captures change |
| `review-gate` | Includes staged, unstaged, and untracked content, runs both lanes, and catches seeded actionable defects | The complete fixture fingerprint remains unchanged |

Keep forward-test fixtures outside the repository. Do not install dependencies, touch user configuration, contact production systems, post external reviews, or leave browser sessions and temporary artifacts running. Record current results in [native-workflow-forward-test-report.md](native-workflow-forward-test-report.md).

## Installation after migration

The five packages use short functional identifiers and `Codex · …` OpenAI display names. They remain explicit-only and independently installable. Install each package from this catalog with the repository's normal skill installer:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill spec-interview
npx skills add https://github.com/17-sss/agent-skills --skill reviewed-plan
npx skills add https://github.com/17-sss/agent-skills --skill completion-loop
npx skills add https://github.com/17-sss/agent-skills --skill visual-match
npx skills add https://github.com/17-sss/agent-skills --skill review-gate
```

Start a new Codex task after installation so skill discovery does not retain stale definitions.

## Known native differences

- Without Goal mode, Codex Completion Loop can preserve the completion contract only inside the current task; it cannot promise cross-task automatic continuation.
- Plan mode is a semantic boundary, not a separate filesystem sandbox. Codex Reviewed Plan requires an effective read-only permission mode for independent gates and uses content fingerprints only as defense in depth.
- Native subagents inherit the parent permission mode. A writable implementation turn therefore cannot claim an isolated review merely by prompting the child to stay read-only; Codex Completion Loop uses a separately sandboxed native Codex run or remains incomplete.
- Browser and Product Design capabilities vary by Codex surface and installed plugins. Codex Visual Match degrades to repository-native automation and reports missing visual evidence.
- Native `/review` is sufficient for an ordinary isolated review. Codex Review Gate deliberately spends more tokens on two independent lanes and returns `INCONCLUSIVE` if that evidence cannot be collected.
- Generated-image approval naturally spans turns because image generation can end the generation turn.
