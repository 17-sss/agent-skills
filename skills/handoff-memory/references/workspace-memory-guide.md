# Workspace Memory Guide

Use workspace scope when the agent session starts from a parent folder that coordinates multiple repositories and the task spans more than one repo.

## Recommended Files

- `_memory/HANDOFF.md`
  - Current cross-repo progress
  - Active blockers
  - Next actions that require coordination

- `_memory/WORKSPACE.md`
  - Workspace purpose
  - Repo map and ownership
  - Shared run commands
  - Environment assumptions

- `_memory/DECISIONS.md`
  - Cross-repo architecture decisions
  - Interface contracts
  - Policies that affect more than one repo

- `_memory/PATTERNS.md`
  - Repeated implementation conventions
  - Naming, API, deployment, and release patterns

## Update Rules

- Update `_memory/HANDOFF.md` when the active cross-repo task changes
- Update `_memory/WORKSPACE.md` when the workspace shape or shared operating model changes
- Update `_memory/DECISIONS.md` when a decision affects multiple repos
- Update `_memory/PATTERNS.md` when a convention should be reused in future work

## Relationship to Repo-Level Handoffs

- Keep repo-specific implementation details in each repo's `docs/HANDOFF.md`
- Keep only cross-repo coordination and durable shared context at the workspace level
- Avoid duplicating detailed repo-level notes in workspace memory unless they affect coordination
