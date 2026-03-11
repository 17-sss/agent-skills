# Agent Skills

A collection of reusable skills for AI coding agents. Skills are packaged instructions and helper scripts that extend agent capabilities while keeping the workflow repository-friendly.

This repository is modeled as a multi-skill catalog, similar to `vercel-labs/agent-skills`, so more skills can be added over time without changing the top-level layout.

## Available Skills

### handoff-memory

Agent-neutral workflow for creating and maintaining shared repo-local HANDOFF documents.

**Use when:**
- Writing a project handoff before ending a session
- Resuming work from an existing handoff
- Standardizing shared project-state notes in Git-trackable files
- Keeping mutable handoff state out of `.codex`, `.claude`, `.windsurf`, or `.agents`

**Behavior:**
- Reuses an existing shared handoff file such as `docs/HANDOFF.md`, `memories/HANDOFF.md`, or `HANDOFF.md`
- Defaults to `docs/HANDOFF.md` when no shared handoff file exists
- Supports global or project-local skill installation, while keeping the shared data inside the repository

## Installation

Install the collection with:

```bash
npx skills add 17-sss/agent-skills
```

If your installer expects a path inside a multi-skill repository, install:

```bash
skills/handoff-memory
```

## Usage

Once installed, agents can invoke the skill when a task calls for project handoff creation, refresh, or recovery.

## Repository Structure

Each skill lives under `skills/<skill-name>/` and may contain:

- `SKILL.md` - Primary skill definition
- `README.md` - Human-facing documentation
- `AGENTS.md` - Agent-facing repo guidance for the skill package
- `metadata.json` - Catalog metadata
- `scripts/` - Helper scripts
- `references/` - Supporting docs and templates
- `agents/` - Optional agent-specific metadata such as `openai.yaml`
