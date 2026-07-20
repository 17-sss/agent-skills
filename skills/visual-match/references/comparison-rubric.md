# Visual Match Comparison Rubric

Inspect the rendered reference and implementation before consulting code. Compare at the same state and viewport.

## Priority

- **Blocking** — prevents use, hides content, breaks the accepted interaction, or creates a serious accessibility failure
- **Major** — materially changes hierarchy, layout, readability, responsive behavior, branding, or component state
- **Minor** — low-impact polish or alignment difference that does not change task success

Fix blocking differences first, then major differences. Continue minor polish only while the acceptance criteria require it or the next pass has a concrete hypothesis.

## Categories

Review:

- page and component geometry
- hierarchy and content grouping
- typography family, size, weight, line height, and wrapping
- semantic colors, contrast, borders, shadows, and elevation
- spacing, alignment, radius, and density
- assets, icons, and image treatment
- default, hover, focus, active, disabled, loading, empty, error, and success states
- responsive reflow, clipping, overflow, and touch behavior
- visible interaction and motion behavior

## Difference record

For each material difference, record:

| Priority | Category | Observed difference | Evidence | Code hypothesis | Next check |
| --- | --- | --- | --- | --- | --- |

Distinguish observation from hypothesis. Validate the hypothesis in code or the rendered state before editing broadly.

## Pixel evidence

Use pixel diff to locate hotspots, not to decide meaning. Normalize viewport, fonts, animation, dynamic data, and capture timing first. When the user supplies an exact tolerance, report the metric and capture conditions; otherwise do not invent a score or pass threshold.

## Final verdict

Pass only when:

- all accepted viewports and states have fresh captures
- no blocking difference remains
- every major difference is fixed, explicitly accepted by the user, or explicitly removed from scope
- functional and code validation passes
- remaining minor differences are listed rather than hidden

If a blocking or major difference cannot be resolved, return `BLOCKED` or `INCOMPLETE` with the evidence and minimum missing capability or decision. A documented blocker is an honest outcome, not a visual-parity pass.
