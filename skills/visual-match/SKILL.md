---
name: visual-match
description: Implement or restyle a runnable interface against an approved image, generated reference, or live-URL baseline through repeated screenshot comparison and verified repair. Use when the user invokes $visual-match, asks for faithful screenshot or URL matching, or makes visual parity part of a completion contract.
---

# Visual Match

Recommended invocation: `Use $visual-match to match <visual target> under <completion criteria>.`

Use this workflow for strict reference matching. Use a general interface-design workflow when no fixed visual target exists.

Read [capability-routing.md](references/capability-routing.md) before choosing tools, [visual-verdict-contract.md](references/visual-verdict-contract.md) before the first comparison, and [comparison-rubric.md](references/comparison-rubric.md) before judging a render.

## Establish the reference contract

Accept one of:

- a user-provided image
- an image generated for this task and explicitly approved by the user
- a user-provided live URL captured at a defined state

Record:

- the reference path or URL
- viewport dimensions and device scale when relevant
- route, data, authentication, and component state
- visible interactions that must match
- expected responsive states
- known exclusions such as backend behavior, personalized data, third-party widgets, or inaccessible states

Treat a live reference as non-mutating by default. Prefer a local or staging fixture. Do not submit forms, make purchases, change settings or permissions, delete data, or trigger any other external state change while capturing or verifying a reference. Authentication or persistence does not authorize production mutations; require separate explicit, narrowly scoped authorization before any state-changing live interaction.

For a generated reference, use an available image-generation capability only when a raster mockup materially clarifies the target. If image generation ends the current turn, obtain explicit approval of the generated image before implementation on the next turn. Do not begin the frontend implementation until approval is present.

## Inspect the repository

Before editing, inspect:

- applicable instructions and design documents
- framework, routes, and rendering model
- styling system, tokens, fonts, assets, and component library
- existing reusable components and states
- development, screenshot, interaction-test, lint, typecheck, test, and build commands

Preserve established design-system boundaries. Do not introduce a new styling layer when the existing system can represent the target.

## Implement through a visual evidence loop

Maintain the visual target, acceptance criteria, evidence loop, completion audit, and blocker rules directly in the current task. Do not hand the loop to a separate persistence skill; this package must remain independently usable.

Before editing, prove that an available capability can render and capture both the reference and implementation at every required viewport and state. Keep captures in a task-scoped temporary location or an existing ignored artifact directory. If equivalent capture is unavailable, offer the minimal isolated Chromium bootstrap from the capability-routing contract. State its network, disk, and cache effects and require explicit user approval unless renderer installation was already authorized; invoking this skill is not installation approval. Never change the target repository's manifests, lockfiles, or `node_modules`, install a branded browser or system packages, or use elevated privileges as part of this fallback. After an approved bootstrap, require a disposable screenshot smoke check. If approval is declined or the isolated browser cannot run, stop before editing and return a concrete `BLOCKED` result. Never claim parity from code inspection.

Create one evidence directory per task. Prefer an existing ignored artifact root for work that must survive another turn; otherwise use a task-scoped temporary directory. Keep the approved reference, capture conditions, and numbered iteration directories together. Never store mutable task evidence inside this installed skill or an agent configuration directory, and never add evidence artifacts to version control unless the user asks.

After reference approval, one smallest runnable candidate may be implemented when no candidate exists. From that point forward, do not make another UI edit until the latest candidate has a valid native visual verdict:

1. Capture the current candidate at every accepted viewport and state.
2. Inspect each reference/candidate pair together through a native image-capable surface at the highest useful detail. Compare rendered evidence before consulting implementation code. Diagnose from outside in: capture frame, major page regions and landmarks, component geometry, typography and wrapping, then surfaces, assets, and local polish.
3. Record a compact landmark table for each target when geometry differs. Measure visible edges or centers such as the header bottom, main-column sides, sidebar bounds, card tops, navigation bar, and floating controls. Do not infer exact CSS values from pixels; use the table to localize drift and verify direction.
4. Produce the structured evidence required by the visual verdict contract. The reviewer is read-only and must not edit files.
5. For equivalent same-size PNG captures supported by the bundled comparator, run the secondary pixel report after direct paired-image inspection. Use its changed bounds, hotspots, and optional heatmap to find residual regions; do not let it override the native verdict.
6. Run the bundled semantic scorer on the native evidence. From iteration 2 onward, pass the previous report with `--previous`.
7. Treat the validated report as the edit gate. A missing or invalid report prohibits the next UI edit.
8. If the verdict is `revise`, convert its blocking and major differences, plus any material minor differences, into the next bounded edit plan. Tie every edit to a reported difference and concrete next check.
9. Apply one coherent repair batch, then recapture every affected viewport and state before making another UI edit. A batch may resolve several reported difference IDs when they share a root cause or belong to the same responsive component; it must not include unrelated speculative cleanup.
10. If the verdict is `fail`, first repair capture equivalence or re-ground a category mismatch. Return `BLOCKED` only when the required evidence or correction is genuinely unavailable.
11. Continue until every target passes or a concrete blocker prevents a safe, testable correction.

A non-pass verdict must report all currently identifiable material differences in one comparison. Later verdicts should verify requested fixes, unresolved differences, and regressions introduced by those fixes rather than introduce unrelated preferences. Preserve a difference ID while the same issue remains unresolved.

If the score fails to improve and the same material difference survives two consecutive repair iterations, stop broad editing and re-check capture conditions, fonts, data, layout assumptions, and the associated code hypothesis. If the same blocker survives three evidence-backed attempts without a new correction path, return `BLOCKED` with the iteration evidence instead of cycling.

Use pixel diff or image overlays only as secondary localization evidence. Anti-aliasing, font rendering, dynamic content, and animation can produce pixel noise; semantic visual review remains authoritative unless the user supplied an exact numeric tolerance.

When the scorer first returns a pass candidate, freeze the candidate and perform one fresh final paired-image audit before completion. Inspect the raw pairs without the prior score, prior reasoning, pixel report, or implementation source. Explicitly check repeated container boundaries and grouping, major landmarks, typography and wrapping, responsive navigation, and visible controls. Prefer a fresh read-only reviewer when native delegation is both available and authorized; otherwise repeat the audit in the current native image surface with the prior verdict set aside. If the audit finds a blocking or major difference, record it in a new numbered evidence file, validate the non-pass report, and resume the repair loop. The skill must not require delegation or another installed skill.

For the first verdict, run:

```bash
python3 <visual-match-skill-dir>/scripts/score_visual_match.py <evidence.json>
```

For each later verdict, run:

```bash
python3 <visual-match-skill-dir>/scripts/score_visual_match.py \
  <evidence.json> \
  --previous <previous-report.json>
```

For equivalent supported PNGs, run after visually inspecting the raw pair:

```bash
python3 <visual-match-skill-dir>/scripts/compare_png.py \
  <reference.png> \
  <candidate.png> \
  --heatmap <iteration-dir>/pixel-heatmap.png \
  --output <iteration-dir>/pixel-report.json
```

Both helpers use only the Python standard library. The semantic scorer validates the paired-image evidence and required difference-to-suggestion links, calculates weighted target scores, uses the lowest target as both `score` and `visual_similarity_percent`, and reports progress against the previous iteration. It does not inspect images; a score without prior native paired-image inspection is invalid evidence. The PNG comparator validates dimensions, calculates a tolerance-based pixel metric, and reports changed bounds and grid hotspots. It supports non-interlaced 8-bit grayscale, RGB, grayscale-alpha, and RGBA PNGs. Do not alter the fixed semantic weights or default `90` threshold during implementation. Use a different semantic threshold only when the user established it before the comparison loop.

Record `pixel_similarity_percent` separately when the bundled comparator or another already available deterministic image metric can compare equivalent captures. Report its method, tolerance, and capture conditions. If the capture format is unsupported, report the metric as `null`; do not install a dependency merely to obtain it. Never blend pixel similarity into `visual_similarity_percent` or substitute it for semantic review.

## Encode reusable decisions

Represent the successful match through the repository's existing reusable surfaces where applicable:

- semantic colors and state tokens
- spacing and layout rules
- typography scale and weights
- radius, border, shadow, and elevation tokens
- reusable component variants and interaction states
- responsive behavior

Avoid turning one screenshot into global design rules without evidence that the rules generalize.

## Verify completion

Before completing the visual goal:

- capture fresh evidence for every required viewport and state
- complete the fresh final paired-image audit after the first validated pass candidate
- include every final native visual verdict, the validated aggregate report, and the lowest overall `score` / `visual_similarity_percent`
- require equivalent captures, `score >= 90` (or a threshold accepted before implementation), category match, high confidence, and zero blocking or major differences
- verify the primary visible interaction path
- confirm no blocking overflow, clipping, overlap, unreadable text, or broken focus behavior remains
- run applicable targeted tests, typecheck, lint, build, and runtime checks
- review the final diff
- list remaining visual differences and why they are accepted, blocked, or out of scope

The score helper returns only a visual pass candidate. Functional validation and the completion audit remain mandatory. An ineligible comparison yields a `fail` visual verdict and must not be presented as a fidelity score. An unresolved blocking or major difference yields `BLOCKED` or `INCOMPLETE`, not success. Do not claim visual parity from code inspection, a self-authored score without paired-image review, pixel similarity, or passing static checks alone.
