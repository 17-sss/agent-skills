---
name: design-loop
description: Build and iteratively refine runnable product interfaces through rendered screenshots, interaction checks, and selective image generation. Use for new or existing UI, frontend, dashboards, admin, landing pages, or game screens; Product Design-assisted concepts; responsive validation; visual alternatives; or reusable design-rule extraction.
---

# Design Loop

Turn interface work into an evidence loop:

`inspect -> implement -> run -> capture -> review -> interact -> fix -> verify`

Operate on the rendered product, not code alone. Adapt the loop to the browser, screenshot, image-input, and image-generation capabilities available in the current agent surface.

## Boundaries

- Preserve the user's requested mode. For audit-only or review-only requests, inspect and report without editing.
- Treat an existing `DESIGN.md`, design system, component library, token set, and product brief as constraints rather than optional inspiration.
- When Product Design is explicitly invoked or design exploration is the primary task, use the optional routing in [surface-capability-guide.md](references/surface-capability-guide.md) before implementation. Keep the package usable when that plugin is unavailable.
- Use a durable design-source workflow or the repository's established design-doc workflow when the main task is defining product direction before implementation.
- Use a strict visual-matching workflow when the user provides an approved screenshot, mockup, or live URL and pixel fidelity is the acceptance criterion.
- Use image generation for raster assets that materially improve the product. Reuse existing icons, logos, illustrations, and code-native design primitives before generating replacements.
- Do not claim visual quality, responsive correctness, or successful interaction without inspecting fresh rendered evidence.

## Workflow

### 1. Frame the target

Identify:

- requested screen, route, component, or user journey
- whether the task is build, improve, audit, compare, or extract rules
- primary user and task
- content and behavior that must remain unchanged
- target desktop and mobile viewports
- acceptance criteria and stop condition

Use conservative assumptions when missing details do not materially change the result. Ask only when a missing choice would create a substantially different product or destructive change.

### 2. Discover the local design contract

Before editing, inspect the closest relevant sources:

- `AGENTS.md` and repository instructions
- `DESIGN.md`, product briefs, specs, screenshots, and visual references
- routes, layouts, components, stories, fixtures, and representative states
- theme files, CSS variables, tokens, typography, icons, and assets
- build, dev-server, test, lint, and typecheck commands

Prefer existing components and tokens. Distinguish observed rules from inferred preferences. If the repository has no design contract, state a small set of task-local assumptions instead of inventing a new design system.

When the user explicitly asks for current design principles, references, or best practices, research current primary or authoritative sources after inspecting the local contract. Cite the sources used, translate them into task-specific decisions, and do not replace the product's established identity with generic trends.

Read the relevant section of [surface-capability-guide.md](references/surface-capability-guide.md) when Product Design, a special capture surface, renderer recovery, image generation, audit, alternatives, or design-rule extraction is needed. Ordinary local rendering and interaction checks can follow this workflow directly.

For ordinary rendering, reuse an existing browser or repository screenshot harness and inspect the captured pixels. Prefer repository-defined viewports; otherwise start with desktop `1440 x 900` and mobile `390 x 844`. Keep route, seed data, account state, viewport, scroll position, and relevant open state stable across comparisons. If the current session cannot inspect screenshots, report that verification gap.

If no existing capability can render and capture the target, follow [Optional Chromium Bootstrap](references/surface-capability-guide.md#optional-chromium-bootstrap). Offer a minimal isolated Chromium bootstrap only with explicit user approval unless installation was already authorized; the skill invocation alone is not installation approval. Do not modify the target repository's manifests, lockfiles, or `node_modules`. If capture remains unavailable, report the exact visual verification gap.

### 3. Capture the baseline

For an existing interface:

1. Start the application with the repository's supported command.
2. Navigate to the exact target state.
3. Capture the current desktop and mobile views before major visual edits.
4. Reproduce the primary interaction or visible defect.
5. Note runtime, console, network, or hydration failures that affect the rendered result.

For a new interface, capture the first functional render before beginning the polish loop.

Use the same data, route, viewport, and UI state for before-and-after comparisons. Keep transient screenshots outside tracked source unless the repository or user asks to preserve them.

### 4. Build a coherent first pass

- Make the primary task functional before polishing secondary surfaces.
- Reuse the current framework, styling system, components, and tokens.
- Establish hierarchy, layout, typography, and navigation before decorative effects.
- Include the critical interaction states relevant to the task: default, hover or touch, focus, loading, empty, error, success, disabled, and open or selected states.
- Keep mobile behavior intentional; do not merely shrink the desktop layout.
- Avoid adding dependencies solely for visual polish unless the user requests them.

If a custom bitmap asset is genuinely needed, use the current image-generation capability and then inspect the asset in context. Do not use image generation to replace an established icon set, logo system, SVG component, or CSS-native visual.

### 5. Review rendered evidence

Read [visual-review-rubric.md](references/visual-review-rubric.md). Inspect every target viewport, apply its blocking/major/minor severity model, and review the rendered image before consulting DOM, styles, or component code. Do not infer visual success from a passing build.

### 6. Exercise the user journey

Test the shortest representative flow end to end:

- click or tap the primary controls
- verify keyboard order, visible focus, and escape or dismissal behavior where applicable
- inspect hover-only behavior separately from touch behavior
- exercise menus, dialogs, drawers, tabs, forms, validation, and navigation that belong to the flow
- check loading, empty, error, and success states when the task exposes them
- watch for console errors, failed requests, layout shifts, and clipped or overflowing content

Use stable selectors and existing test conventions when automating the flow. Do not broaden a visual task into unrelated application repair unless a dependency blocks verification.

### 7. Iterate in bounded passes

Fix one coherent issue cluster at a time, such as hierarchy, spacing, responsive layout, or interaction states. After each pass:

1. Re-render the same route and state.
2. Capture the same target viewports.
3. Compare against the previous evidence.
4. Run the smallest relevant functional check.
5. Keep the change only when it produces a concrete improvement without regression.

Default to two focused improvement passes after the first functional render. Continue only while a blocking or major issue remains and another pass has a clear hypothesis. Avoid an unbounded "make it prettier" loop.

### 8. Optional modes

For audit-only requests, visual alternatives, or reusable design-rule extraction, read the matching section in [surface-capability-guide.md](references/surface-capability-guide.md#alternative-comparison-and-rule-extraction). Keep the same rendered-evidence and interaction standards; do not implement an audit-only request.

### 9. Verify completion

Do not stop until the requested scope has fresh evidence for all applicable items:

- target route builds and renders
- primary journey completes
- desktop and mobile screenshots were inspected
- no blocking overflow, clipping, overlap, or unreadable text remains
- keyboard, focus, hover, touch, and dismissal behavior were checked where relevant
- relevant tests, typecheck, lint, or build checks pass
- remaining gaps and unverified environments are explicit

Finish with a concise report containing changed files, evidence paths, viewports and flows checked, important fixes, validation commands, and remaining risks.

## Prompt Recipes

Read [prompt-recipes.md](references/prompt-recipes.md) when the user wants a reusable invocation template or when the task needs a clearer brief before starting. It includes the full loop plus dedicated game UI, product UI, audit, alternative-comparison, generated-asset, and design-rule recipes.
