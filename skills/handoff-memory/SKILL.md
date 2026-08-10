---
name: handoff-memory
description: Create, refresh, validate, or resume a shared Git-trackable handoff for one repository, a multi-repo workspace, or a named workstream. Use for session checkpoints, project resumption, handoff standardization, stale-note checks, and durable agent-neutral project memory.
---

# Handoff Memory

## Overview

Keep one canonical handoff close to the work it describes. Use the bundled scripts to resolve its path, initialize or refresh it, validate resume usability, detect staleness, and optionally preserve a timestamped snapshot.

This skill is agent-neutral. Install location and data location are separate: shared mutable documents belong in the target repository or workspace, not in `.codex`, `.claude`, `.windsurf`, or `.agents` by default.

## Core Contract

- Keep one canonical handoff per active scope and document type.
- Honor explicit `--handoff-path` and `--workstream` choices before auto-detection.
- Do not infer a workspace-wide task merely because the current directory contains multiple repositories.
- When more than one workstream still matches a resume request, return an ambiguous result instead of guessing.
- On resume, treat `Next Actions` as the default execution queue and `Resume Prompt` as the default framing unless the user or current repository state invalidates them.
- Keep snapshots optional and secondary to the canonical handoff.
- Never store secrets, tokens, private keys, raw credentials, or long confidential logs.
- Prefer project-relative paths; the validator warns about foreign machine-specific absolute paths.

## Prerequisites

- `python3` in `PATH` for the bundled scripts.
- `git` in `PATH` for freshness checks and repository metadata. Path resolution and validation still work outside Git, but freshness evidence is weaker.
- Run the non-interactive scripts directly and use their `--help` output rather than recreating their logic.

## Choose the Scope

| Scope | Use when | Canonical handoff |
| --- | --- | --- |
| Repo | The task belongs to one repository | Existing `docs/HANDOFF.md`, `memories/HANDOFF.md`, or `HANDOFF.md`; otherwise `docs/HANDOFF.md` |
| Workspace | One active concern coordinates multiple repositories | `_memory/HANDOFF.md` |
| Workstream | A workspace contains multiple independent repo combinations or initiatives | `_memory/workstreams/<name>/HANDOFF.md` |

Use `_memory/INDEX.json` as the lightweight workstream index. Companion `WORKSPACE.md`, `WORKSTREAM.md`, `DECISIONS.md`, and `PATTERNS.md` files are durable context, not routine session outputs. Read [workspace-memory-guide.md](references/workspace-memory-guide.md) before choosing or maintaining workspace/workstream structure.

## Default Workflow

### Create or Refresh

1. Resolve or initialize the canonical document:

   ```bash
   python3 scripts/create_handoff.py --project-root <path> --scope auto --document handoff --format json
   ```

   Add `--workstream <name>` for a specific initiative inside a larger workspace. Prefer an explicit `--handoff-path` when the project already defines its canonical location.

2. Read the current document before changing it. Preserve still-valid context and remove stale claims that would mislead the next session.

3. Update the current truth, not a transcript. Keep `TL;DR`, `Current Objective`, `Next Actions`, validation state, risks, and the smallest useful quick-reference set current.

4. Validate before ending the session:

   ```bash
   python3 scripts/validate_handoff.py --project-root <path> --scope auto --document handoff
   ```

   Add `--strict` only when strict template conformance should fail on missing sections, placeholders, or empty required sections.

### Resume

1. Resolve the actual resume target before planning or editing:

   ```bash
   python3 scripts/resolve_handoff_path.py --project-root <path> --scope auto --document handoff --resume --format json
   ```

2. Stop for clarification if the result is ambiguous. Otherwise read the selected handoff and check staleness:

   ```bash
   python3 scripts/check_staleness.py --project-root <path> --scope auto --document handoff
   ```

3. Compare the notes with current repository evidence and call out drift. In mixed workspaces, validate only the selected workstream or repositories named by the handoff unless the user explicitly asks for `--workspace-wide` status.

4. Execute the first unfinished `Next Actions` item. Explore only as needed to complete it; do not replace a still-valid handoff with a fresh design pass.

5. Refresh and validate the canonical handoff again when material state changed.

Read [agent-usage-best-practices.md](references/agent-usage-best-practices.md) for the complete start-, during-, and end-of-session behavior and resume selection priority.

## Content Rules

- Make the document understandable in under a minute and start with a strong `TL;DR`.
- Prefer exact project-relative paths, commands, dates, and repository names over vague prose.
- Record confirmed current state; mark unverified claims explicitly.
- State what changed recently, what remains risky, and what should happen next.
- Keep implementation detail in repo handoffs, workspace coordination in the workspace handoff, and initiative-specific coordination in its workstream.
- Touch companion documents only when durable shared context changes.
- Include a short resume checklist and only the files, commands, dashboards, or docs needed to continue.

Use [handoff-template.md](references/handoff-template.md) when creating or substantially restructuring a document.

## Optional Snapshots

Create a snapshot only for a meaningful transition such as a risky migration, deploy boundary, major context transfer, debugging checkpoint, or substantial handoff rewrite. Always provide both `--snapshot-kind` and `--snapshot-reason`:

```bash
python3 scripts/create_handoff.py \
  --project-root <path> \
  --scope auto \
  --document handoff \
  --snapshot \
  --snapshot-kind handoff \
  --snapshot-reason "Context transfer before ending the session"
```

Read [snapshot-strategy.md](references/snapshot-strategy.md) for supported kinds, naming, workstream examples, and when to skip a snapshot.

## Script Responsibilities

- `scripts/resolve_handoff_path.py`: resolve repo, workspace, or workstream paths; honor explicit overrides; apply ambiguity-safe resume selection; optionally ensure a file exists.
- `scripts/create_handoff.py`: initialize or refresh canonical content and metadata; update `_memory/INDEX.json`; optionally archive a timestamped snapshot.
- `scripts/validate_handoff.py`: check resume usability, placeholders, required sections, length, and portability; use `--strict` for template enforcement.
- `scripts/check_staleness.py`: compare handoff metadata with relevant Git activity without scanning unrelated child repositories by default.

## Reference Routing

Read only the reference needed for the current task:

- [agent-usage-best-practices.md](references/agent-usage-best-practices.md): normal start, resume, update, and close-out behavior.
- [workspace-memory-guide.md](references/workspace-memory-guide.md): workspace versus workstream selection, index fields, companion documents, and narrowed validation.
- [handoff-template.md](references/handoff-template.md): expected sections and document intent.
- [snapshot-strategy.md](references/snapshot-strategy.md): snapshot decisions, kinds, commands, and naming.
- [agent-integrations.md](references/agent-integrations.md): install locations for Codex and other agents. Installation never changes the shared-data rule.
