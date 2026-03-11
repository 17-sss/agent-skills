---
name: handoff-memory
description: Create, refresh, and consume shared repo-local HANDOFF documents so work can continue across agent sessions, contributors, or machines. Use when asked to write a handoff, checkpoint progress, resume prior work, or standardize project-state notes in a Git-trackable file such as `docs/HANDOFF.md`.
---

# Handoff Memory

## Overview

Keep one shared HANDOFF document inside the project repository. Use it to preserve the current state, decisions, risks, and next actions so another agent session or contributor can resume quickly.

Resolve the file path first, read the current HANDOFF if it exists, then update it with the latest state. Keep the document concise, action-oriented, and safe to commit.

## Workflow

1. Resolve the canonical file path.
   Run `scripts/resolve_handoff_path.py --project-root <repo> --ensure --format json`.

2. Read the existing HANDOFF before making changes.
   If the file exists, preserve still-valid context and remove stale claims that would mislead the next session.

3. Update the document using the template in `references/handoff-template.md`.
   Replace placeholders with the current repository state, active objective, commands run, verification status, and next actions.

4. Save the file inside the repository.
   Reuse an existing shared handoff path when present. Otherwise create `docs/HANDOFF.md`.

5. Re-read the final file and verify it answers the restart questions:
   What is the current goal?
   What changed?
   What is blocked or risky?
   What should happen next?

## Scope Boundary

- Treat this skill as the HANDOFF workflow definition, not as a scheduler.
- Installation scope and data location are separate concerns.
- The skill may be installed globally or per-project, but the shared mutable HANDOFF should stay inside the repository.
- Agent-specific files such as `AGENTS.md`, `CLAUDE.md`, `.codex/*`, or `.windsurf/rules/*` may reference the shared HANDOFF, but should not become the primary mutable handoff store.

## Path Rules

- Prefer an explicit `--handoff-path` override when the project already defines a shared handoff location.
- Otherwise reuse an existing shared repo-local handoff file in a recognized location such as `docs/HANDOFF.md`, `memories/HANDOFF.md`, or `HANDOFF.md`.
- If no recognized file exists, create `docs/HANDOFF.md`.
- Avoid `.codex`, `.claude`, `.windsurf`, or `.agents` as the default shared handoff location.
- Keep one canonical HANDOFF per project. Avoid creating multiple competing files.

## Content Rules

- Keep the document short enough to scan in under a minute.
- Prefer exact file paths, branch names, commands, and dates over vague prose.
- Record what is true now, not a transcript of the full chat.
- Include unfinished work, failed attempts that matter, and what still needs verification.
- Do not store secrets, tokens, private keys, raw credentials, or long confidential logs.
- Note when a claim is unverified.
- If the codebase drifted from the previous HANDOFF, overwrite stale sections instead of appending contradictory notes.

## Recommended Sections

Use the template in `references/handoff-template.md`. Keep these sections unless there is a strong reason to remove one:

- Metadata
- Current Objective
- Current State
- Important Context
- Changes Made
- Validation
- Open Questions / Risks
- Next Actions
- Resume Prompt

## Resume Workflow

When asked to continue work from a prior session:

1. Resolve the canonical HANDOFF path.
2. Read the HANDOFF before planning or editing code.
3. Compare the document against the current repo state and call out drift.
4. Continue the work.
5. Refresh the HANDOFF again before ending the session if anything material changed.

## Example Triggers

- "Write a HANDOFF for this project."
- "Save the current state so another session can pick this up."
- "Resume from the shared project handoff."
- "Keep the handoff in the repository, not in an agent-specific folder."
- "Checkpoint this work for another PC."

## Resources

### `scripts/resolve_handoff_path.py`
Resolve the canonical repo-local HANDOFF path from the repository root. Use `--handoff-path` to honor a project-specific override. Use `--ensure` to create the file when it does not exist.

### `references/handoff-template.md`
Use this template to initialize or refresh the HANDOFF content. Load it when the file is missing, stale, or structurally inconsistent.

### `references/agent-integrations.md`
Use this when the user asks where to install the skill for Codex or another agent. Keep install notes out of the core workflow when they are not needed.

## Notes

- This skill standardizes the handoff workflow and structure. It does not replace project docs such as `README.md`, `CHANGELOG.md`, or architecture notes.
- For multi-PC setups, commit the shared HANDOFF file with the repository when appropriate instead of storing the primary state in a machine-local folder.
