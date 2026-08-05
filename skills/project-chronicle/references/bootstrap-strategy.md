# Bootstrap an Existing Project Chronicle

Use this workflow when the project already has meaningful history but no trustworthy long-term chronicle.

## 1. Establish scope

Confirm the repository or workspace boundary, requested historical depth, and output location from repository instructions or the user. Do not silently scan unrelated sibling repositories.

For a very old or large repository, bootstrap in explicit eras. A bounded, honest first pass is better than an apparently complete narrative built from truncated evidence.

## 2. Build the source map

Inspect repository instructions and likely authorities before reading large Git ranges:

- root README and documentation index
- architecture, product, operations, deployment, schema, ADR, glossary, release, and migration docs
- existing `HISTORY.md`, `CHANGELOG.md`, handoffs, work logs, and archived plans
- package manifests, service boundaries, tests, and current entry points
- Git tags, releases, merge commits, and repository-hosted PR or issue metadata when available

Run `collect_history_evidence.py --since auto`. On a first bootstrap, `auto` has no lower anchor and collects up to the configured cap.

## 3. Identify real periods

Cluster evidence by actual workstream boundaries rather than keyword frequency alone. Useful boundaries include:

- a product or service becoming usable
- a platform, storage, deployment, or domain-model migration
- a major reliability or security correction
- a new repository or package boundary
- a reversal or replacement of a prior direction
- an incident whose lesson changed future work

Merge repeated same-theme changes across adjacent dates. Record explicit start and end dates supported by the evidence. Do not claim precision that the sources do not provide.

## 4. Reconstruct without inventing

For each candidate period, separate:

- **Verified:** directly supported by current files, commits, tags, PRs, issues, or dated documents.
- **Supported inference:** multiple sources make the explanation likely, but no source states it directly.
- **Unknown:** the rationale, alternative, ownership, or boundary cannot be recovered.

Current code proves the present implementation, not the original motive. A commit subject proves that a contributor recorded a change, not that every sentence in it remains true.

## 5. Interview only for missing human context

Do not ask the user to recall commit hashes, file locations, dates, or current implementation details that tools can establish.

Ask one question at a time only when the answer would materially change:

- the reason a direction was chosen
- the intended project or product boundary
- an important rejected alternative
- the meaning of an overloaded domain term
- whether a contradiction represents a reversal, a bug, or stale documentation

Show the evidence already found and recommend the best-supported interpretation when possible. Preserve unanswered questions in `GAPS.md` instead of blocking all useful history work.

## 6. Write the layered history

Create or refresh:

1. `README.md` with origins, project map, eras, coverage, source authorities, and reading paths.
2. `TIMELINE.md` with consolidated workstream periods.
3. `LOG.md` with the bootstrap record and full current `HEAD` anchor.
4. Detailed entries only for material events whose context cannot fit cleanly in the timeline.
5. `GAPS.md` only for unresolved, consequential history.

If the working tree contains relevant uncommitted changes, describe them separately and keep the anchor at the current committed `HEAD`.

## 7. Verify coverage

- Confirm whether the collector truncated commits or documents.
- Verify cited commits exist and belong to the current repository ancestry.
- Compare the earliest claimed period with the earliest available evidence.
- Check that every detailed entry is reachable from the overview or timeline.
- Run the validator in strict mode and inspect the final diff.

Report incomplete ranges explicitly. Never label a partial scan as the complete project history.
