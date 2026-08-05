---
name: project-chronicle
description: Reconstruct, maintain, read, and audit a durable, evidence-backed project history for humans and AI. Use when asked to explain how a repository evolved, recover historical context from Git and existing documents, preserve the background and reasoning behind meaningful changes, record recurring project progress, create a long-term project chronicle, or make an older codebase understandable after months or years.
---

# Project Chronicle

Build Git-trackable history that explains what exists, how it evolved, why meaningful changes happened, and where the supporting evidence lives. Keep this history useful after the current task, session, branch, and contributors are gone.

Do not produce a commit-by-commit transcript. Record every chronicle run in a lightweight log, then consolidate related changes into periods and workstreams for long-term comprehension.

## Core contract

- Investigate repository facts before asking the user.
- Treat current code and configuration as evidence of current behavior, not automatic proof of historical intent.
- Label claims as verified, supported inference, or unknown when the distinction matters.
- Ask one material background, intent, or trade-off question at a time. Give a recommended answer when evidence supports one.
- Prefer explicit date ranges, milestones, and workstreams over repetitive daily chronology.
- Record repository-relative paths and resolvable commit, tag, PR, issue, release, or document anchors.
- Never invent rationale to make the history appear complete.
- Preserve detailed history separately from current operational state and next-action documents.
- Keep shared mutable history inside the target repository or workspace, not in agent-specific configuration folders.
- Do not expose secrets, raw credentials, private keys, or confidential logs.

## Select the mode

Choose the narrowest mode that satisfies the request:

1. **Bootstrap** — reconstruct history for an existing project that has no usable chronicle.
2. **Record** — capture changes since the last recorded commit and refresh the durable narrative.
3. **Read or audit** — explain existing history, trace a decision, or check chronicle drift without editing unless the user also asks for a refresh.

Use `references/bootstrap-strategy.md` for Bootstrap. Use `references/recording-rules.md` for Record. Read `references/document-model.md` before creating or substantially restructuring the target documents. Read `references/history-entry-template.md` when a detailed milestone, decision, migration, incident, discovery, or deprecation entry is justified.

## Resolve the history location

Honor an explicit user or repository convention first. Otherwise reuse an existing `docs/project-history/` or `docs/history/` only when it already serves the same long-term-history purpose. Default to `docs/project-history/`.

Do not repurpose `CHANGELOG.md`: release-facing change lists do not replace project background and reasoning. Treat `HISTORY.md`, ADRs, decision logs, architecture docs, release notes, issue trackers, and HANDOFF files as evidence or linked authorities unless the repository already declares one of them to be the canonical project history.

Use this default target model:

```text
docs/project-history/
├── README.md
├── TIMELINE.md
├── LOG.md
├── entries/
│   └── YYYY-MM[-DD]-<slug>.md
└── GAPS.md
```

Always maintain `README.md`, `TIMELINE.md`, and `LOG.md`. Create `entries/` and `GAPS.md` lazily when detail or unresolved history warrants them.

## Collect evidence

Run the bundled collector before reconstructing or recording history:

```bash
python3 <skill-dir>/scripts/collect_history_evidence.py \
  --project-root <path> \
  --since auto \
  --format json
```

`--since auto` reads the `project-chronicle:last-recorded-commit` marker from `LOG.md`. With no marker, it collects the available history up to the commit cap and reports truncation honestly. Git commits and working-tree status are scoped to `--project-root`, including when it is a subdirectory of a larger worktree; for a subdirectory scope, include only tags whose tagged commit directly changes that scope. Use explicit `--since`, `--until`, and `--max-commits` ranges to investigate large histories without pretending a partial scan is complete; `git.head` remains the actual checkout HEAD while `git.range_until` identifies the selected upper revision.

Inspect, in order of relevance:

- applicable `AGENTS.md` or repository instructions
- root README and documentation indexes
- current architecture, operations, ADR, decision, glossary, release, and history documents
- current code, configuration, tests, schemas, and deployment files needed to verify claims
- Git status, commits, tags, merge points, changed paths, and blame or file history when useful
- existing HANDOFF or session snapshots as time-bounded evidence, not unquestioned current truth

If the repository is not in Git, continue from its documents and files. State that commit ancestry and change coverage could not be verified.

## Reconcile evidence

Use each source for what it can actually prove:

- Current code, configuration, and tests: what the repository does now.
- Current authoritative documents: intended contracts, operating model, and declared boundaries.
- Git commits, tags, releases, PRs, and issues: sequence, authorship context, and recorded change rationale.
- Old handoffs and snapshots: what a contributor believed at that point in time.
- User answers: intent, organizational context, rejected alternatives, and undocumented reasoning.

When sources disagree, preserve the contradiction and its dates. Do not silently choose the most convenient narrative. Ask the user only after repository evidence cannot resolve a material ambiguity.

## Write for layered reading

Maintain three levels:

1. `README.md` — a five-minute orientation: purpose, origins, what exists, history coverage, eras, source-of-truth map, and reading guide.
2. `TIMELINE.md` — a concise period-level narrative grouped by workstream or milestone.
3. `LOG.md` and `entries/` — one lightweight record per chronicle run plus detailed evidence-backed narratives only where background matters.

Every Bootstrap or Record run must add one dated `LOG.md` record. If there was no material historical change, record a short review entry and say so; do not fabricate a milestone. Update `TIMELINE.md` only when the period-level story changes. Update `README.md` only when durable background, the project map, coverage, or recommended reading path changes.

Keep this marker near the top of `LOG.md`:

```md
<!-- project-chronicle:last-recorded-commit: <full-commit-hash-or-none> -->
```

The marker represents the latest committed history covered by the chronicle. Dirty working-tree evidence must be labeled uncommitted and must not advance the marker beyond `HEAD`.

## Keep history distinct from handoff state

Project history answers: what exists, where it came from, why it changed, what alternatives mattered, and what consequences followed.

Operational handoff material answers: what is true now, what is in progress, what is risky, and what should happen next.

Link between them when useful, but do not copy a long historical recap into a handoff or turn the chronicle into a next-action queue. An existing ADR or canonical technical document owns its detailed contract; the chronicle should summarize historical significance and link to it instead of duplicating it.

## Validate before reporting completion

Run the bundled validator after creating or refreshing the history:

```bash
python3 <skill-dir>/scripts/validate_project_history.py \
  --project-root <path> \
  --strict
```

Resolve every error. Review warnings and either fix them or explain why they are acceptable. Also run `git diff --check` and inspect the final diff. Do not commit unless the user asks.

Report:

- history path
- coverage and latest recorded commit
- documents created or updated
- verified periods or workstreams
- remaining gaps, contradictions, and uncommitted evidence
- validation commands and results

## Bundled resources

- `scripts/collect_history_evidence.py` — collect bounded Git and documentation evidence as JSON or a concise summary.
- `scripts/validate_project_history.py` — validate document structure, anchors, portability, links, entry names, and obvious secret material.
- `references/document-model.md` — define the target file responsibilities and starter structures.
- `references/bootstrap-strategy.md` — reconstruct an existing project without flattening it into commit chronology.
- `references/recording-rules.md` — record every run while keeping the long-term narrative compact.
- `references/history-entry-template.md` — write a detailed historical entry only when the additional context is durable and material.
