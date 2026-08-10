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

Read [surface-capability-guide.md](references/surface-capability-guide.md) before choosing the Product Design, render, screenshot, interaction, or image-generation path.

If no existing capability can render and capture the applicable target, offer a minimal isolated Chromium bootstrap before treating visual verification as unavailable. State the network download, disk use, and cache location, and require explicit user approval unless the user already authorized installing a renderer. The skill invocation alone is not installation approval. Do not modify the target repository's manifests, lockfiles, or `node_modules`; do not install a branded browser or system packages; and do not use elevated privileges. After an approved bootstrap, prove it with a disposable screenshot smoke check. If approval is declined or the isolated browser cannot run, continue only with separately valid non-visual work and report the exact visual verification gap.

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

### 8. Compare alternatives only when useful

Create alternatives when the user asks for them or when one consequential visual decision remains genuinely uncertain.

- Produce two or three variants, not an open-ended gallery.
- Keep content, behavior, viewport, and data constant.
- Compare them with the same rubric and user task.
- Select a winner based on evidence, not novelty.
- Remove unused implementation artifacts unless the user asks to retain them.

Do not use A/B exploration to delay an obvious fix.

### 9. Extract reusable rules when requested

When a successful result should guide future screens, summarize:

- palette and semantic color use
- typography hierarchy
- spacing and layout rhythm
- radius, border, elevation, and motion rules
- component variants and interaction states
- responsive adaptations
- accessibility constraints
- imagery and iconography guidance

Update an existing authoritative design document when one exists. If none exists, use the repository's design-document convention or a dedicated design-source workflow rather than silently introducing a new source of truth.

### 10. Verify completion

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
