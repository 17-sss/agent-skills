# Project Chronicle Document Model

Use this model when creating a new chronicle or restructuring an unusable one. Preserve a stronger repository convention when it already separates orientation, period-level history, and detailed evidence.

## Reading layers

The documents serve different reading speeds:

- `README.md`: orient a new human or agent in about five minutes.
- `TIMELINE.md`: scan the project's eras, milestones, and workstreams.
- `LOG.md`: prove that each chronicle run was recorded and establish the incremental Git anchor.
- `entries/*.md`: explain background, rationale, alternatives, and consequences for material events.
- `GAPS.md`: preserve unknown or contradictory history without contaminating verified narrative.

History is not automatically the authority for current runtime behavior. Link the current code and canonical documentation that own those contracts.

## `README.md`

Keep these sections:

```md
# Project History

## Purpose and Origins

Explain why the project exists, the problem it originally addressed, and the context that shaped it. Mark reconstruction or uncertainty explicitly.

## What Exists

Map the major products, repositories, services, packages, domains, or workflows. Link to current authoritative documents rather than reproducing them.

## Historical Eras

- `YYYY-MM ~ YYYY-MM` — Era name: one-sentence significance.

## History Coverage

- Earliest verified evidence:
- Latest recorded commit:
- Reconstructed ranges:
- Known incomplete ranges:

## Current Sources of Truth

- Runtime behavior:
- Architecture:
- Operations:
- Domain language:
- Decisions:

## Reading Guide

- Start with:
- For <topic>:
- For detailed evidence:

## Evidence Policy

State how verified facts, supported inference, unknown history, and uncommitted evidence are labeled.
```

Do not turn the overview into another implementation manual. Keep the source map current and let the linked files own detail.

## `TIMELINE.md`

Group related work into explicit periods:

```md
# Project Timeline

## 2026-06-02 ~ 2026-06-19 — Initial density workflow

- **Context:** What problem or phase drove the work.
- **Evolution:** The meaningful change across the period.
- **Outcome:** What became possible or stable.
- **Evidence:** `abc1234`, `docs/architecture.md`, [detailed entry](entries/2026-06-density-workflow.md).
```

Prefer one coherent period over several near-identical daily entries. Split a period when its goal, architecture, ownership, or outcome materially changes.

## `LOG.md`

Keep the machine-readable anchor and one lightweight record per Bootstrap or Record run:

```md
# Project History Log

<!-- project-chronicle:last-recorded-commit: 0123456789abcdef0123456789abcdef01234567 -->

## 2026-08-03 — Authentication boundary recorded

- Type: record
- Period: 2026-07-21 ~ 2026-08-03
- Summary: Added a detailed history entry and extended the authentication workstream period.
- Evidence: `0123456789abcdef0123456789abcdef01234567`, `src/auth/`, `docs/adr/0007-auth-boundary.md`
- Detailed entry: [Authentication boundary redesign](entries/2026-08-auth-boundary-redesign.md)
- Uncommitted evidence: none
```

For a no-material-change review, add a short record with `Type: review`, name the evidence checked, and leave the timeline unchanged.

## `GAPS.md`

Create this only when gaps exist:

```md
# Project History Gaps

## GAP-001 — Original queue choice

- Period: before 2024-05
- Status: unknown
- Why it matters: Future maintainers may mistake the current queue for an arbitrary choice.
- Evidence checked: Git history begins after the decision; current docs contain no rationale.
- Needed to resolve: Confirmation from an original maintainer or an archived design document.
```

Close a gap without erasing it. Add the resolution, date, source, and links to any timeline or detailed entry updated as a result.

## Portability and safety

- Use repository-relative paths.
- Prefer full commit hashes in the log anchor and short hashes in prose only when unambiguous.
- Do not embed local session transcripts or large generated evidence dumps.
- Do not record credentials, private URLs containing tokens, customer data, or confidential raw logs.
- Keep external links descriptive and record a repository-local source when one exists.
