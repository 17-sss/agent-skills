# Skill classification and installation

Runtime reviewed: 2026-08-30. Display groups updated: 2026-09-03.

Classify a skill by the minimum runtime surface required to satisfy its own completion contract. Origin, inspiration, OpenAI UI metadata, and optional acceleration do not make a skill Codex-only.

- `Codex`: the skill cannot honestly reach its success verdict without a Codex-specific Goal, review, sandboxed execution, or native subagent contract.
- `Cross-agent`: the core workflow can complete with common files, shell commands, Git, GitHub APIs, browser automation, image input, or equivalent capabilities exposed by multiple agents.

Keep runtime compatibility separate from display grouping. Codex-dependent workflows remain in `Codex`; cross-agent skills use `Planning`, `Design`, `Git Workflow`, and `Project Memory` groups. `Experimental` takes precedence over the purpose group for skills still being validated, currently the Godot game-development skill `godot-dev-loop`. It describes maturity, not a runtime restriction; behavior and interfaces may change.

## Audited inventory

| Display group | Runtime | Skill | Minimum runtime reason |
| --- | --- | --- | --- |
| Codex | Codex | `reviewed-plan` | Requires fresh native Codex Architect and Critic reviewers behind enforced read-only isolation |
| Codex | Codex | `completion-loop` | Requires an isolated read-only Codex review before implementation completion |
| Codex | Codex | `milestone-runner` | Reconciles durable milestones with native Codex Goal tools and the completed goal object |
| Codex | Codex | `review-gate` | Requires two independent native Codex review lanes with tool-enforced isolation |
| Design | Cross-agent | `design-loop` | Uses rendered UI evidence and adapts to available browser, screenshot, and image capabilities |
| Experimental | Cross-agent | `godot-dev-loop` | Uses repository files, Bash, Git, Godot 4.x real-window capture, image inspection, and fresh non-interactive runner processes without requiring one agent's native workflow tools |
| Planning | Cross-agent | `spec-interview` | The interview, read-only inspection, and specification work without an agent-exclusive command; delegation is optional |
| Design | Cross-agent | `visual-match` | Uses equivalent screenshots, browser automation, image evidence, and a package-local standard-library scorer |
| Project Memory | Cross-agent | `handoff-memory` | Uses Git-trackable documents and filesystem operations |
| Project Memory | Cross-agent | `project-chronicle` | Uses Git, repository documents, filesystem operations, and package-local standard-library evidence and validation helpers |
| Git Workflow | Cross-agent | `github-pr-review` | Uses `gh`, local Git, tests, and GitHub REST or GraphQL APIs |
| Git Workflow | Cross-agent | `github-pr-publish` | Uses `gh`, local Git, and GitHub REST APIs |
| Git Workflow | Cross-agent | `commit-helper` | Uses local Git and package-local Python helpers |

The `.claude-plugin/marketplace.json` file mirrors the display groups in this table for the `skills` CLI. The CLI title-cases plugin names such as `git-workflow` and `project-memory` and displays one group per skill. These labels do not restrict which agent a user can choose and do not determine the destination directory.

`npx skills list --global` reads the `pluginName` recorded in the global skill lock at installation time. Changing this repository's manifest does not refresh an existing installation. After publishing the grouping change, re-add the affected installed skills from the repository with their existing agent selections. Group-only changes may not trigger `skills update`, which checks skill-folder content changes.

## Codex installation paths

Select Codex explicitly when installing a Codex-dependent workflow:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill reviewed-plan --agent codex
```

The current [skills CLI supported-agent table](https://github.com/vercel-labs/skills#supported-agents) defines these Codex destinations:

| Scope | Command flag | Destination |
| --- | --- | --- |
| Project | default | `.agents/skills/<skill-name>` |
| Global | `--global` | `~/.codex/skills/<skill-name>` |

Therefore `.agents/skills/` is the expected Codex project path, even for a Codex-only skill. Do not create a project `.codex/skills/` workaround merely because the skill belongs to the `Codex` TUI group. Use `--agent codex` to choose the runtime and `--global` to choose the user-wide Codex directory.

Cross-agent skills can still be installed only for Codex:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill visual-match --agent codex
```

Or they can be installed for every supported agent:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill visual-match --agent '*'
```

## Maintenance rule

Re-audit a package when its success gate, required tool, delegation model, or sandbox contract changes. When a classification changes, update together:

- `.claude-plugin/marketplace.json`
- `README.md` and `README.ko.md`
- this dependency matrix
- `CODEX_SKILL_NAMES`, `CROSS_AGENT_SKILL_NAMES`, `TUI_SKILL_GROUPS`, and applicable local validation inventories in `scripts/check-native-workflow-skills.py`
- grouping and standalone contract tests

When experimental status changes, also align the package's `SKILL.md` description and status note, `metadata.json` abstract, existing README, and `agents/openai.yaml` display name and short description. Keep the published skill directory and invocation name unchanged.

Run the offline acceptance checks after every change:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/check-native-workflow-skills.py --require-validator
npx --yes skills add . --list
```
