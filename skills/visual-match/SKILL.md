---
name: visual-match
description: Implement or restyle a runnable interface against an approved image, generated reference, or live-URL baseline through repeated screenshot comparison and verified repair. Use when the user invokes $visual-match, asks for faithful screenshot or URL matching, or makes visual parity part of a Goal-mode completion contract.
---

# Visual Match

Recommended invocation: `/goal <visual target and completion criteria>. Use $visual-match.`

Use this workflow for strict reference matching. Use a general interface-design workflow when no fixed visual target exists.

Read [capability-routing.md](references/capability-routing.md) before choosing tools and [comparison-rubric.md](references/comparison-rubric.md) before judging a render.

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

For a generated reference, use the native image-generation skill or tool only when a raster mockup materially clarifies the target. Image generation may end the current turn; on the next turn, obtain explicit approval of the generated image before implementation. Do not begin the frontend implementation until approval is present.

## Inspect the repository

Before editing, inspect:

- applicable instructions and design documents
- framework, routes, and rendering model
- styling system, tokens, fonts, assets, and component library
- existing reusable components and states
- development, screenshot, interaction-test, lint, typecheck, test, and build commands

Preserve established design-system boundaries. Do not introduce a new styling layer when the existing system can represent the target.

## Implement through a visual evidence loop

Maintain the visual goal, acceptance criteria, evidence loop, completion audit, and blocker rules directly in the current task. Do not hand the loop to a separate persistence skill; this package must remain independently usable during migration.

Before editing, prove that an available capability can render and capture both the reference and implementation at every required viewport and state. Keep captures in a task-scoped temporary location or an existing ignored artifact directory. If equivalent capture is unavailable, stop before editing and return a concrete `BLOCKED` result; do not install a browser, plugin, or dependency implicitly and do not claim parity from code inspection.

1. Capture a baseline at the recorded route, viewport, data, and UI state.
2. Implement the smallest coherent visual or interaction change.
3. Render and capture the same state again.
4. Compare the reference and result using the rubric. Rank blocking and major differences before minor polish.
5. Translate each material difference into a concrete code hypothesis.
6. Fix one related difference cluster, then recapture the same state.
7. Exercise visible interactions and responsive states that belong to the accepted scope without mutating external reference state.
8. Continue while a material mismatch has a safe, testable correction.

Use pixel diff or image overlays only as secondary localization evidence. Anti-aliasing, font rendering, dynamic content, and animation can produce pixel noise; semantic visual review remains authoritative unless the user supplied an exact numeric tolerance.

Do not invent or tune an arbitrary visual score. A pass requires the recorded acceptance criteria to be satisfied and all remaining differences to be explicitly classified.

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
- verify the primary visible interaction path
- confirm no blocking overflow, clipping, overlap, unreadable text, or broken focus behavior remains
- run applicable targeted tests, typecheck, lint, build, and runtime checks
- review the final diff
- list remaining visual differences and why they are accepted, blocked, or out of scope

An unresolved blocking or major difference yields `BLOCKED` or `INCOMPLETE`, not success. Do not claim visual parity from code inspection or passing static checks alone.
