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
2. Inspect each reference/candidate pair together through a native image-capable surface at the highest useful detail. Compare rendered evidence before consulting implementation code.
3. Produce the structured evidence required by the visual verdict contract. The reviewer is read-only and must not edit files.
4. Run the bundled scorer on that evidence. From iteration 2 onward, pass the previous report with `--previous`.
5. Treat the validated report as the edit gate. A missing or invalid report prohibits the next UI edit.
6. If the verdict is `revise`, convert its blocking and major differences, plus any material minor differences, into the next bounded edit plan. Tie every edit to a reported difference and concrete next check.
7. Fix one related difference cluster, then recapture the same viewport and state before making another UI edit.
8. If the verdict is `fail`, first repair capture equivalence or re-ground a category mismatch. Return `BLOCKED` only when the required evidence or correction is genuinely unavailable.
9. Continue until every target passes or a concrete blocker prevents a safe, testable correction.

A non-pass verdict must report all currently identifiable material differences in one comparison. Later verdicts should verify requested fixes, unresolved differences, and regressions introduced by those fixes rather than introduce unrelated preferences. Preserve a difference ID while the same issue remains unresolved.

If the score fails to improve and the same material difference survives two consecutive repair iterations, stop broad editing and re-check capture conditions, fonts, data, layout assumptions, and the associated code hypothesis. If the same blocker survives three evidence-backed attempts without a new correction path, return `BLOCKED` with the iteration evidence instead of cycling.

Use pixel diff or image overlays only as secondary localization evidence. Anti-aliasing, font rendering, dynamic content, and animation can produce pixel noise; semantic visual review remains authoritative unless the user supplied an exact numeric tolerance.

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

The helper uses only the Python standard library. It validates the paired-image evidence and required difference-to-suggestion links, calculates weighted target scores, uses the lowest target as both `score` and `visual_similarity_percent`, and reports progress against the previous iteration. It does not inspect images; a score without prior native paired-image inspection is invalid evidence. Do not alter the fixed weights or default `90` threshold during implementation. Use a different threshold only when the user established it before the comparison loop.

Record `pixel_similarity_percent` separately only when an already available deterministic image metric can compare equivalent captures. Report its method and capture conditions. Never blend it into `visual_similarity_percent`, install a dependency merely to obtain it, or substitute it for semantic review.

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
- include every final native visual verdict, the validated aggregate report, and the lowest overall `score` / `visual_similarity_percent`
- require equivalent captures, `score >= 90` (or a threshold accepted before implementation), category match, high confidence, and zero blocking or major differences
- verify the primary visible interaction path
- confirm no blocking overflow, clipping, overlap, unreadable text, or broken focus behavior remains
- run applicable targeted tests, typecheck, lint, build, and runtime checks
- review the final diff
- list remaining visual differences and why they are accepted, blocked, or out of scope

The score helper returns only a visual pass candidate. Functional validation and the completion audit remain mandatory. An ineligible comparison yields a `fail` visual verdict and must not be presented as a fidelity score. An unresolved blocking or major difference yields `BLOCKED` or `INCOMPLETE`, not success. Do not claim visual parity from code inspection, a self-authored score without paired-image review, pixel similarity, or passing static checks alone.
