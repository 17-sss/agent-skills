# Detailed History Entry Template

Create a detailed entry only when a future reader needs more than the period-level timeline can carry. Suitable types include milestone, architecture, decision, migration, incident, discovery, deprecation, and operating-model change.

Name the file `YYYY-MM-<slug>.md` for a period or `YYYY-MM-DD-<slug>.md` for a dated event.

```md
# <Descriptive event or period title>

- Period: YYYY-MM-DD ~ YYYY-MM-DD
- Type: milestone | architecture | decision | migration | incident | discovery | deprecation | operations
- Evidence status: verified | mixed | supported inference
- Anchors: `<full-or-short-commit>`, `<tag>`, `<repo-relative-path>`, `<PR-or-issue-link>`

## Context

Explain the earlier state, problem, constraint, or opportunity that made the change meaningful.

## What Changed

Describe the durable change at the product, domain, architecture, operational, or workflow level. Avoid diff narration.

## Why

Record directly supported rationale. Label inference. If the reason is unknown, say so and link the matching gap.

## Alternatives and Trade-offs

Include only alternatives that were actually considered or are documented. Do not manufacture an architecture comparison after the fact.

## Outcome and Consequences

Explain what became possible, what constraints remained, what later work depended on this, and whether the direction was subsequently replaced.

## Evidence

- Commits:
- Tags / releases:
- PRs / issues:
- Documents:
- Code / configuration / tests:
- Human confirmation:

## Unknowns

- State unresolved rationale, date, ownership, or contradiction.
- Use `None known` only after checking the relevant evidence.
```

Link the entry from `TIMELINE.md` and, when it changes the high-level reading map, from `README.md`.
