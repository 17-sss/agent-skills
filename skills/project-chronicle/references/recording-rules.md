# Record Ongoing Project History

Use this workflow after the initial chronicle exists.

## Incremental evidence

Run the collector with `--since auto`. It reads the full commit anchor from `LOG.md` and returns commits through the requested `--until`, normally `HEAD`.

Before writing:

- verify that the anchor resolves in the current repository
- note whether the branch diverged from the recorded lineage
- inspect dirty, staged, and untracked paths separately from committed history
- read existing periods and entries before creating another one

If the recorded anchor is missing from the current repository, stop incremental assumptions. Determine whether history was rewritten, the chronicle was copied from another repository, or the checkout is incomplete.

## Record every run without bloating the narrative

Every Bootstrap or Record run adds one `LOG.md` section.

Choose one type:

- `bootstrap` — first reconstruction of existing history
- `record` — meaningful committed or explicitly labeled uncommitted change
- `review` — evidence checked with no material narrative change
- `correction` — prior historical claim corrected or confidence changed
- `gap-resolution` — previously unknown history resolved with new evidence

A routine review does not deserve a new timeline period. Say what was checked and that no material change was found.

## Decide whether to update the timeline

Update the current period when the new work shares the same goal, boundaries, and outcome trajectory. Extend its end date and revise the synthesis rather than appending near-duplicate bullets.

Create a new period when at least one material boundary changes:

- goal or user outcome
- architecture or data ownership
- product or repository boundary
- operational model
- major risk posture
- prior approach was reversed or replaced

Use a detailed entry only when future readers need the background, rationale, alternatives, consequences, or evidence set beyond the timeline summary.

## Maintain the overview sparingly

Update `README.md` only when one of these changes:

- project purpose or origin understanding
- major component or repository map
- historical era boundaries
- history coverage or confidence
- current source-of-truth map
- recommended reading path

Do not rewrite the overview for ordinary implementation progress.

## Advance the anchor safely

Set `project-chronicle:last-recorded-commit` to the full `HEAD` hash whose committed history is covered after the update.

- Do not use a dirty-tree pseudo hash.
- Label dirty evidence as uncommitted in the log record.
- If only uncommitted work was recorded, keep the marker at `HEAD`.
- If the user later commits that work, the next run records the resulting commit normally.

## Correct history transparently

Do not silently erase a material historical claim. Update the affected overview, period, or entry, then add a `correction` log record explaining:

- the prior claim
- the new evidence
- the corrected interpretation
- remaining uncertainty

Git preserves the textual diff; the correction record preserves why it changed.

## Finish

Run strict validation, `git diff --check`, and a final diff review. Report coverage, anchor, documents changed, gaps, contradictions, and whether any cited evidence remains uncommitted.
