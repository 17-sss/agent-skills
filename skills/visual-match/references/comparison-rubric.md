# Visual Match Comparison Rubric

Inspect the rendered reference and implementation before consulting code. Compare at the same state and viewport.

## Capture equivalence gate

Set `capture_equivalent` to `true` only when the reference and candidate use the accepted viewport and device scale, route and scroll position, data and locale, theme, fonts, animation point, and visible UI state. If any material condition cannot be aligned, set it to `false`. The target and overall `visual_similarity_percent` must then be `null`, and the visual verdict is `fail` until equivalent evidence exists.

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

## Paired-image component score

Score each accepted viewport and state only after inspecting the reference and candidate together. Use these fixed components:

| Component | Maximum points |
| --- | ---: |
| `layout_geometry` | 30 |
| `typography` | 15 |
| `color_surface` | 15 |
| `spacing_shape` | 10 |
| `assets_content` | 10 |
| `responsive_states` | 10 |
| `interaction_states` | 10 |

Assign an integer from 0 through 100 to every component. Use the anchors consistently without reverse-engineering a passing total:

| Range | Evidence meaning |
| --- | --- |
| `95–100` | No observable mismatch or only trivial local noise |
| `90–94` | Minor differences remain but hierarchy and fidelity are preserved |
| `70–89` | At least one major mismatch materially changes fidelity |
| `40–69` | Several severe mismatches dominate the component |
| `0–39` | The component is missing, unusable, or fundamentally wrong |

A component that is absent from the accepted scope still receives 100 when both images consistently omit it. Do not hide missing evidence by omitting a component. If the captures are not equivalent, set the entire `component_scores` value to `null` and fix the comparison conditions before scoring.

Every component below 100 needs a difference in the same category. Every reported difference must lower that component below 100. Select scores from rendered evidence before inspecting implementation details.

The bundled scorer calculates each target as:

```text
earned component points = component weight × component score ÷ 100
target score = round(100 × earned component points ÷ applicable maximum points)
overall score = visual_similarity_percent = minimum target score
```

Using the lowest target prevents a strong desktop render from masking a weak mobile or interaction state. The required evidence schema and command are defined in `visual-verdict-contract.md`.

The default threshold is `90`. A different `--threshold` is valid only when the user established it before implementation. `visual_pass_candidate` is true only when every capture is equivalent, the lowest score meets the threshold, category match and confidence are high, and no blocking or major difference remains. It is not the final functional verdict.

## Pixel evidence

Use pixel diff to locate hotspots, not to decide meaning. Normalize viewport, fonts, animation, dynamic data, and capture timing first. Calculate `pixel_similarity_percent` only with an already available deterministic metric. Report the metric name, version when known, ignored regions or tolerance, and capture conditions. If no such tool exists, set the value and method to `null`; do not install a package or weaken standalone operation merely to obtain it.

Never average pixel similarity into the paired-image score. Pixel noise can be high while the product meaning matches, and a high pixel score can still hide a missing interaction or inaccessible state.

## Score record

Combine the validated native verdict with the optional pixel metric and workflow verdict:

```json
{
  "capture_equivalent": true,
  "score": 96,
  "verdict": "pass",
  "category_match": true,
  "visual_similarity_percent": 96,
  "pixel_similarity_percent": null,
  "pixel_metric": null,
  "blocking_differences": 0,
  "major_differences": 0,
  "minor_differences": 2,
  "confidence": "high",
  "verdict": "PASS"
}
```

## Final verdict

Pass only when:

- all accepted viewports and states have fresh captures
- every comparison is equivalent and the lowest paired-image score meets the accepted threshold
- every target matches the intended visual category
- confidence is high and the score helper returns `visual_pass_candidate: true`
- no blocking difference remains
- every major difference is fixed, explicitly accepted by the user, or explicitly removed from scope
- functional and code validation passes
- remaining minor differences are listed rather than hidden

If capture equivalence is false, the visual verdict is `fail` and no fidelity score is valid. Fix the missing comparison condition before editing the UI. If a blocking or major difference cannot be resolved, return `BLOCKED` or `INCOMPLETE` with the evidence and minimum missing capability or decision. A documented blocker is an honest outcome, not a visual-parity pass.
