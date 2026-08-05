# Skill classification and installation

Reviewed: 2026-07-23

Classify a skill by the minimum runtime surface required to satisfy its own completion contract. Origin, inspiration, OpenAI UI metadata, and optional acceleration do not make a skill Codex-only.

- `Codex`: the skill cannot honestly reach its success verdict without a Codex-specific Goal, review, sandboxed execution, or native subagent contract.
- `Other`: the core workflow can complete with common files, shell commands, Git, GitHub APIs, browser automation, image input, or equivalent capabilities exposed by multiple agents.

## Audited inventory

| Group | Skill | Minimum runtime reason |
| --- | --- | --- |
| Codex | `reviewed-plan` | Requires fresh native Codex Architect and Critic reviewers behind enforced read-only isolation |
| Codex | `completion-loop` | Requires an isolated read-only Codex review before implementation completion |
| Codex | `milestone-runner` | Reconciles durable milestones with native Codex Goal tools and the completed goal object |
| Codex | `review-gate` | Requires two independent native Codex review lanes with tool-enforced isolation |
| Other | `design-loop` | Uses rendered UI evidence and adapts to available browser, screenshot, and image capabilities |
| Other | `spec-interview` | The interview, read-only inspection, and specification work without an agent-exclusive command; delegation is optional |
| Other | `visual-match` | Uses equivalent screenshots, browser automation, image evidence, and a package-local standard-library scorer |
| Other | `handoff-memory` | Uses Git-trackable documents and filesystem operations |
| Other | `project-chronicle` | Uses Git, repository documents, filesystem operations, and package-local standard-library evidence and validation helpers |
| Other | `github-pr-review` | Uses `gh`, local Git, tests, and GitHub REST or GraphQL APIs |
| Other | `github-pr-publish` | Uses `gh`, local Git, and GitHub REST APIs |
| Other | `commit-helper` | Uses local Git and package-local Python helpers |

The `.claude-plugin/marketplace.json` file mirrors this table for the `skills` CLI selection screen. Its `codex` and `other` plugin names are display groups only. They do not restrict which agent a user can choose and do not determine the destination directory.

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
- `CODEX_SKILL_NAMES` and `OTHER_SKILL_NAMES` in `scripts/check-native-workflow-skills.py`
- grouping and standalone contract tests

Run the offline acceptance checks after every change:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/check-native-workflow-skills.py --require-validator
npx --yes skills add . --list
```
