# handoff-memory

Install this skill from GitHub with:

```bash
npx skills add <owner>/handoff-memory
```

This repository is intentionally structured as a single root skill so tools such as `skills.sh` can detect `SKILL.md` at the repository root.

The skill can be installed globally or per-project. The installation location does not change where the shared HANDOFF file lives.

## What It Does

`handoff-memory` keeps one shared HANDOFF document inside the repository:

- Prefer an existing shared handoff file such as `docs/HANDOFF.md`, `memories/HANDOFF.md`, or `HANDOFF.md`
- Otherwise create `docs/HANDOFF.md`
- Keep agent-specific files as references to the shared handoff, not as the primary mutable state

## Install Scope

### Codex

- Global install: `$CODEX_HOME/skills/handoff-memory` or `~/.codex/skills/handoff-memory`
- Project-local install: `<repo>/.codex/skills/handoff-memory`

### Other Agents

- Claude Code: keep agent-specific instructions in `CLAUDE.md` or `.claude/`, but point them at the shared repo-local HANDOFF
- Windsurf: keep rules in `.windsurf/rules/`, but point them at the shared repo-local HANDOFF
- Generic fallback: if no standard install path exists, `.agents/skills/handoff-memory` is an acceptable neutral install location

## Shared Data Rule

The primary handoff file should stay inside the repository so it can be reviewed and synchronized with Git when appropriate. Installing this skill on another machine copies the workflow, while the shared project state remains in the repo.
