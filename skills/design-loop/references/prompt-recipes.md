# Prompt Recipes

Invoke the skill explicitly with `$design-loop`, or describe a matching visual implementation task and let the current agent select it.

## Full Visual Design Loop

```text
Use $design-loop as the visual builder for [project or screen].
Inspect the repository's design contract, build the smallest coherent version,
run it locally, and capture desktop and mobile states. Review hierarchy, spacing,
contrast, typography, responsiveness, interaction clarity, and the primary user flow.
Fix blocking and major issues, capture fresh evidence after each focused pass,
use image generation only for justified raster assets, and compare alternatives only
when a consequential decision remains uncertain. Finish with validation evidence and
extract reusable design rules when requested.
```

## Build a New Interface

```text
Use $design-loop to build [screen or flow] for [target user].
Preserve [framework, components, brand rules, or behavior].
The primary task is [user task].
Run the product, inspect desktop and mobile renders, exercise the primary flow,
and iterate until the rendered evidence and relevant checks pass.
```

## Improve an Existing Screen

```text
Use $design-loop to improve [route or component] without changing [protected behavior].
Capture the current state first, rank visible issues by user impact, fix the major issues,
and verify the same desktop and mobile states after each focused pass.
```

## Game UI

```text
Use $design-loop to build or improve [game screen or HUD] from the player's perspective.
Verify HUD readability, icon and action clarity, gameplay obstruction, state legibility,
touch reachability, and desktop/mobile behavior. Reuse existing game assets first;
generate portraits, backgrounds, or other raster art only when needed. Exercise the
representative interaction loop and repeat screenshot review until major issues are resolved.
```

## Product UI

```text
Use $design-loop to build or improve [SaaS dashboard, admin screen, or product flow]
for [target user]. Preserve the existing product language and behavior. If current design
principles or references are requested, research authoritative sources and cite the decisions
derived from them. Run the product, inspect desktop and mobile hierarchy, spacing, navigation,
readability, and critical states, then verify that a first-time user can complete [primary task].
```

## Review Without Editing

```text
Use $design-loop in audit-only mode for [route or flow].
Inspect rendered desktop and mobile states and exercise [interaction].
Return blocking, major, and minor findings with screenshot evidence; do not modify files.
```

## Compare Alternatives

```text
Use $design-loop to create [two or three] alternatives for [specific decision].
Keep content, data, behavior, and viewports constant.
Compare task clarity, hierarchy, readability, responsiveness, interaction clarity,
and product consistency, then apply the best-supported option.
```

## Use a Generated Asset

```text
Use $design-loop to determine whether [screen] needs a custom raster asset.
Reuse existing product assets when possible. If a new asset is justified, use image generation,
integrate it into the real layout, and re-check hierarchy, contrast, loading, and responsiveness.
```

## Extract Design Rules

```text
Use $design-loop to inspect the successful implementation of [screens].
Extract reusable palette, typography, spacing, component-state, responsive,
accessibility, and imagery rules into the repository's existing design source of truth.
```

## Useful Constraints

Add only constraints that matter to the task:

- exact routes and states to inspect
- target desktop and mobile viewports
- content or behavior that must not change
- primary user and user journey
- supported browsers or devices
- accessibility target
- whether variants or image generation are allowed
- maximum iteration budget
- required test, typecheck, lint, or build commands
