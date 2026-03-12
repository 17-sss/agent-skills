---
name: handoff-memory
description: Create, refresh, and consume shared HANDOFF and memory documents for either a single repository or a multi-repository workspace. Use when asked to write a handoff, checkpoint progress, resume prior work, or standardize project-state notes in Git-trackable files such as `docs/HANDOFF.md` for a repo or `_memory/HANDOFF.md` for a workspace root.
---

# Handoff Memory

## Overview

Keep shared memory documents close to the work they describe. For a single repository, store the primary handoff in the repo. For a multi-repository workspace, store cross-repo memory in the workspace root.

Resolve the scope first, read the current document if it exists, then update it with the latest state. Keep each document concise, action-oriented, and safe to commit.

## Workflow

1. Resolve the canonical file path.
   Run `scripts/resolve_handoff_path.py --project-root <path> --ensure --format json`.

2. Read the existing HANDOFF before making changes.
   If the file exists, preserve still-valid context and remove stale claims that would mislead the next session.

3. Choose the right document for the scope.
   For a repo, use the handoff template.
   For a workspace, use the workspace handoff plus companion memory documents when needed.

4. Update the document using the matching template.
   Replace placeholders with the current state, active objective, commands run, verification status, and next actions.

5. Save the file inside the repository or workspace root.
   Reuse an existing shared path when present. Otherwise create the default file for the chosen scope and document type.

6. Re-read the final file and verify it answers the restart questions:
   What is the current goal?
   What changed?
   What is blocked or risky?
   What should happen next?

## Scope Boundary

- Treat this skill as the HANDOFF workflow definition, not as a scheduler.
- Installation scope and data location are separate concerns.
- The skill may be installed globally or per-project, but the shared mutable documents should stay inside the repository or workspace root they describe.
- Agent-specific files such as `AGENTS.md`, `CLAUDE.md`, `.codex/*`, or `.windsurf/rules/*` may reference the shared HANDOFF, but should not become the primary mutable handoff store.

## Path Rules

- Prefer an explicit `--handoff-path` override when the project or workspace already defines a shared location.
- In repo scope, reuse an existing shared handoff file in a recognized location such as `docs/HANDOFF.md`, `memories/HANDOFF.md`, or `HANDOFF.md`.
- In workspace scope, keep cross-repo memory under `_memory/`.
- If no repo handoff exists, create `docs/HANDOFF.md`.
- If no workspace handoff exists, create `_memory/HANDOFF.md`.
- For workspace memory, prefer:
  - `_memory/WORKSPACE.md` for goals, structure, and ownership
  - `_memory/HANDOFF.md` for current cross-repo progress
  - `_memory/DECISIONS.md` for architecture and policy decisions
  - `_memory/PATTERNS.md` for repeated implementation conventions
- Avoid `.codex`, `.claude`, `.windsurf`, or `.agents` as the default shared handoff location.
- Keep one canonical memory file per scope and document type. Avoid creating multiple competing files.

## Content Rules

- Keep the document short enough to scan in under a minute.
- Prefer exact file paths, branch names, commands, and dates over vague prose.
- Record what is true now, not a transcript of the full chat.
- Include unfinished work, failed attempts that matter, and what still needs verification.
- Do not store secrets, tokens, private keys, raw credentials, or long confidential logs.
- Note when a claim is unverified.
- If the codebase drifted from the previous HANDOFF, overwrite stale sections instead of appending contradictory notes.

## Recommended Sections

Use the matching template in `references/`. Keep these sections unless there is a strong reason to remove one:

- Metadata
- Current Objective
- Current State
- Important Context
- Changes Made
- Validation
- Open Questions / Risks
- Next Actions
- Resume Prompt

## Workspace Guidance

Use workspace scope when you open the agent from a parent folder that contains multiple repositories and the task spans more than one of them.

- Put cross-repo progress in `_memory/HANDOFF.md`
- Put durable workspace context in `_memory/WORKSPACE.md`
- Put decisions that affect multiple repos in `_memory/DECISIONS.md`
- Put repeatable conventions in `_memory/PATTERNS.md`
- Keep repo-specific implementation details in each repo's own `docs/HANDOFF.md`

## Resume Workflow

When asked to continue work from a prior session:

1. Resolve the canonical HANDOFF path.
2. Read the HANDOFF before planning or editing code.
3. If working in workspace scope, also read companion memory files that matter for the task.
4. Compare the document against the current repo or workspace state and call out drift.
5. Continue the work.
6. Refresh the HANDOFF again before ending the session if anything material changed.

## Example Triggers

- "Write a HANDOFF for this project."
- "Write a workspace handoff for these repos."
- "Save the current state so another session can pick this up."
- "Resume from the shared project handoff."
- "Keep cross-repo memory at the parent folder."
- "Keep the handoff in the repository, not in an agent-specific folder."
- "Checkpoint this work for another PC."

## Resources

### `scripts/resolve_handoff_path.py`
Resolve the canonical repo-local or workspace-local memory path. Use `--scope repo|workspace|auto`, `--document handoff|workspace|decisions|patterns`, or `--handoff-path` to honor an explicit override. Use `--ensure` to create the file when it does not exist.

### `references/handoff-template.md`
Use this template to initialize or refresh a repo or workspace HANDOFF file.

### `references/workspace-memory-guide.md`
Use this when the task spans multiple repositories and you need to decide which workspace-level memory files to update.

### `references/agent-integrations.md`
Use this when the user asks where to install the skill for Codex or another agent. Keep install notes out of the core workflow when they are not needed.

## Notes

- This skill standardizes the handoff workflow and structure. It does not replace project docs such as `README.md`, `CHANGELOG.md`, or architecture notes.
- For multi-PC setups, commit the shared memory files with the repository or workspace when appropriate instead of storing the primary state in a machine-local folder.
