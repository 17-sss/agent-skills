# Native Visual Verdict Contract

Use this contract after every fresh candidate capture and before the next UI edit.

## Reviewer boundary

Inspect the approved reference and current candidate together through a native image-capable surface. Use the highest useful image detail and compare the same viewport and state. Review the raw pair before reading implementation code or consulting a pixel report so code intent and aggregate numbers cannot excuse a visible mismatch.

Use a fresh read-only visual review lane when the current surface and governing instructions authorize one. Otherwise perform the same paired-image inspection in the current agent. The workflow must still work without delegation or another installed skill.

The reviewer may read only the reference contract, capture conditions, current and previous images, and prior unresolved difference IDs. It must not edit files. Its only output is evidence JSON for the bundled scorer. The scorer never sees or judges pixels itself.

## Artifact layout

Keep one task artifact root:

```text
<artifact-root>/visual-match/<task-slug>/
  reference/
    approved.png
    capture-contract.md
  iterations/
    001/
      candidate.png
      evidence.json
      report.json
      pixel-report.json
      pixel-heatmap.png
    002/
      candidate.png
      evidence.json
      report.json
```

Use an existing ignored artifact directory when evidence must survive another turn. Otherwise use a task-scoped temporary directory. Do not write into the installed skill directory, `.agents/`, `.codex/`, dependency folders, or package-manager caches.

Pixel artifacts are optional secondary evidence. Generate them only for equivalent captures supported by the bundled comparator or another already available deterministic metric.

## Evidence schema

Write one evidence file per iteration:

```json
{
  "iteration": 1,
  "targets": [
    {
      "id": "desktop-default",
      "reference_path": "reference/approved.png",
      "candidate_path": "iterations/001/candidate.png",
      "capture_equivalent": true,
      "category_match": true,
      "component_scores": {
        "layout_geometry": 84,
        "typography": 92,
        "color_surface": 96,
        "spacing_shape": 86,
        "assets_content": 95,
        "responsive_states": 94,
        "interaction_states": 93
      },
      "differences": [
        {
          "id": "D1",
          "priority": "major",
          "category": "layout_geometry",
          "observation": "The content column is wider than the approved reference.",
          "evidence": "The candidate right edge extends about one card width beyond the reference."
        }
      ],
      "suggestions": [
        {
          "difference_id": "D1",
          "change": "Constrain the content wrapper before changing child card widths.",
          "next_check": "Recapture the desktop default state and compare both column edges."
        }
      ],
      "reasoning": "The visual category and hierarchy match, but geometry remains materially wider.",
      "confidence": "high"
    }
  ]
}
```

Rules:

- `component_scores` contains every category from the comparison rubric and uses integers from 0 through 100.
- Use `component_scores: null` when `capture_equivalent` is false; do not invent a fidelity score for incomparable images.
- Every score below 100 must have a difference in the same category.
- Every reported difference lowers its category below 100.
- Every difference has a linked suggestion. A passing minor difference may remain documented, but its next check must still be explicit.
- Keep a stable difference ID across iterations until the issue is fixed. Assign a new ID only for a genuinely new mismatch or regression.
- Keep the approved reference path and target IDs stable. Save each candidate to a new numbered artifact path; never overwrite the previous screenshot.
- Report all currently identifiable material differences in the same pass.
- Keep observations visual and evidence-based. Put code hypotheses only in `suggestions`.

## Validated verdict

The scorer returns the measured loop contract:

```json
{
  "score": 87,
  "verdict": "revise",
  "category_match": true,
  "differences": ["[desktop-default][major][layout_geometry][D1] ..."],
  "suggestions": ["[desktop-default][D1] ..."],
  "reasoning": "desktop-default: ...",
  "visual_similarity_percent": 87,
  "visual_pass_candidate": false
}
```

Interpret it as follows:

- `pass` — all captures are equivalent, the lowest score meets the threshold, category match and confidence are high, and no blocking or major difference remains.
- `revise` — the evidence is comparable and a concrete visual repair remains.
- `fail` — evidence is ineligible, the visual category is wrong, or a blocking difference prevents a pass.

`fail` is a visual verdict, not permission to abandon the task. Repair capture equivalence or the blocking mismatch when a safe correction exists; otherwise return an evidence-backed blocker.

## Edit gate

Freeze each validated report before editing. Every next UI edit must cite at least one difference ID from that report. Several cited IDs may be repaired in one coherent batch when they share a root cause or responsive component. Recapture every affected target and produce a new report before another UI edit. Do not reuse approval after candidate code or relevant runtime data changes.

Pass the prior `report.json` through `--previous` on later iterations. Treat a non-positive score delta with repeated material difference IDs as stalled evidence. Re-ground after two consecutive stalled repair iterations and stop after three evidence-backed attempts only when no new correction path exists.

## Fresh pass audit

The first validated pass candidate is provisional. Freeze its implementation and captures, then perform a fresh raw-pair audit without providing the prior verdict, semantic score, pixel report, or implementation source. The audit must explicitly verify:

- page regions, major landmarks, and responsive composition
- repeated card or row boundaries and the grouping they communicate
- typography, wrapping, clipping, and density
- navigation, visible controls, icons, and state

Use a fresh read-only reviewer when native delegation is available and authorized. Otherwise perform a second clean inspection in the current native image surface. This is an independent perspective, not a dependency on another skill.

If the fresh audit finds a blocking or major difference, write a new numbered evidence file with linked suggestions, run the scorer, and resume from that validated report. Complete only when the fresh audit finds no blocking or major difference and the candidate remains unchanged afterward.
