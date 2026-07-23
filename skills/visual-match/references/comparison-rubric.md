# Visual Match Comparison Rubric

Inspect the rendered reference and implementation before consulting code. Compare at the same state and viewport.

## Capture equivalence gate

Set `capture_equivalent` to `true` only when the reference and candidate use the accepted viewport and device scale, route and scroll position, data and locale, theme, fonts, animation point, and visible UI state. If any material condition cannot be aligned, set it to `false`. The target and overall `visual_similarity_percent` must then be `null`, and the verdict is `INCONCLUSIVE` until equivalent evidence exists.

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

## Anchored semantic score

Score each accepted viewport and state with these fixed components:

| Component | Maximum points |
| --- | ---: |
| `layout_geometry` | 30 |
| `typography` | 15 |
| `color_surface` | 15 |
| `spacing_shape` | 10 |
| `assets_content` | 10 |
| `responsive_states` | 10 |
| `interaction_states` | 10 |

Assign exactly one anchored level to every component:

| Level | Factor | Evidence meaning |
| --- | ---: | --- |
| `match` | 1.0 | No observable mismatch in the accepted scope |
| `minor` | 0.9 | Only localized, low-impact differences remain |
| `major` | 0.6 | One material mismatch changes fidelity or clarity |
| `severe` | 0.3 | Multiple material mismatches dominate the component |
| `blocking` | 0.0 | A critical element or state is missing, unusable, or not comparable |
| `not_applicable` | excluded | The accepted target genuinely has no evidence for this component |

Do not use `not_applicable` to hide missing evidence or a mismatch. Record the observed differences and select the level from rendered evidence before inspecting implementation details.

The bundled scorer calculates each target as:

```text
target score = round(100 × earned component points ÷ applicable maximum points)
overall visual_similarity_percent = minimum target score
```

Using the lowest target prevents a strong desktop render from masking a weak mobile or interaction state. Run the helper from the installed skill package:

```bash
python3 <visual-match-skill-dir>/scripts/score_visual_match.py <evidence.json>
```

Input shape:

```json
{
  "targets": [
    {
      "id": "desktop-default",
      "capture_equivalent": true,
      "components": {
        "layout_geometry": "minor",
        "typography": "match",
        "color_surface": "match",
        "spacing_shape": "minor",
        "assets_content": "match",
        "responsive_states": "not_applicable",
        "interaction_states": "match"
      },
      "blocking_differences": 0,
      "major_differences": 0,
      "minor_differences": 2,
      "confidence": "high"
    }
  ]
}
```

The default threshold is `90`. A different `--threshold` is valid only when the user established it before implementation. `visual_pass_candidate` is true only when every capture is equivalent, the lowest score meets the threshold, confidence is high, and no blocking or major difference remains. It is not the final functional verdict.

## Pixel evidence

Use pixel diff to locate hotspots, not to decide meaning. Normalize viewport, fonts, animation, dynamic data, and capture timing first. Calculate `pixel_similarity_percent` only with an already available deterministic metric. Report the metric name, version when known, ignored regions or tolerance, and capture conditions. If no such tool exists, set the value and method to `null`; do not install a package or weaken standalone operation merely to obtain it.

Never average pixel similarity into the anchored semantic score. Pixel noise can be high while the product meaning matches, and a high pixel score can still hide a missing interaction or inaccessible state.

## Score record

Combine the helper output with the optional pixel metric and workflow verdict:

```json
{
  "capture_equivalent": true,
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
- every comparison is equivalent and the lowest anchored semantic score meets the accepted threshold
- confidence is high and the score helper returns `visual_pass_candidate: true`
- no blocking difference remains
- every major difference is fixed, explicitly accepted by the user, or explicitly removed from scope
- functional and code validation passes
- remaining minor differences are listed rather than hidden

If capture equivalence is false, return `INCONCLUSIVE` with the missing comparison condition. If a blocking or major difference cannot be resolved, return `BLOCKED` or `INCOMPLETE` with the evidence and minimum missing capability or decision. A documented blocker is an honest outcome, not a visual-parity pass.
