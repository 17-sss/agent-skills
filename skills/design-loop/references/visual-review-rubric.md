# Visual Review Rubric

Review screenshots as product evidence. Do not score code structure as a proxy for rendered quality.

## Severity

- **Blocking:** task cannot be completed; content or controls are inaccessible; critical state is hidden; navigation is broken.
- **Major:** hierarchy, readability, responsiveness, interaction clarity, or consistency is materially degraded.
- **Minor:** localized polish issue with little effect on task completion.

Fix blocking issues first, then major issues by user impact. Batch minor issues only when they share a clear cause.

## Review Order

### 1. Task clarity

- Is the primary action obvious within a few seconds?
- Does the page communicate what it is and what the user can do next?
- Are clickable and non-clickable elements visually distinct?
- Are critical states and feedback visible near the action that caused them?

### 2. Visual hierarchy

- Is attention directed to the right content first?
- Do heading, body, metadata, and action levels remain distinct?
- Are too many elements competing through size, color, elevation, or motion?
- Does decorative content overpower the user's task?

### 3. Layout and spacing

- Do major regions align to a coherent grid?
- Are repeated gaps drawn from a small, consistent spacing rhythm?
- Are related items grouped more tightly than unrelated items?
- Is density appropriate for the product and viewport?

### 4. Typography and readability

- Is body text readable at the actual rendered size?
- Are line length, line height, and wrapping comfortable?
- Are labels truncated, orphaned, or ambiguous?
- Are numeric, tabular, or status values aligned appropriately?

### 5. Color and contrast

- Does color encode meaning consistently?
- Are text, borders, controls, and focus indicators distinguishable?
- Does the interface remain understandable without color alone?
- When exact accessibility conformance matters, verify contrast with a measurement tool; do not claim a ratio from visual inspection alone.

### 6. Responsive behavior

- Does the layout recompose instead of merely compressing?
- Are tap targets usable and controls reachable on mobile?
- Is horizontal scrolling intentional and limited to appropriate content?
- Do navigation, tables, charts, dialogs, and sticky regions adapt cleanly?
- Are hover-only affordances replaced or exposed for touch?

### 7. Interaction states

- Are hover, focus, active, selected, disabled, loading, success, and error states distinguishable where relevant?
- Can menus and dialogs be opened, traversed, and dismissed predictably?
- Is focus visible and ordered according to the visual flow?
- Does motion clarify state without delaying the task or ignoring reduced-motion preferences?

### 8. Consistency and product fit

- Are components, radii, borders, shadows, icon sizes, and content voice consistent?
- Does the result extend the existing product language rather than importing an unrelated aesthetic?
- Are generic effects such as gratuitous gradients, glass panels, oversized hero copy, or excessive pill shapes used only when the product calls for them?

### 9. Runtime quality

- Are there visible layout shifts, broken assets, hydration errors, or failed requests?
- Does generated imagery load at an appropriate size and quality?
- Are long content, localization, zoom, and real data likely to break the layout?

## Variant Comparison

Compare alternatives under identical conditions. For each candidate, record:

| Criterion | Candidate A | Candidate B | Candidate C |
| --- | --- | --- | --- |
| Primary-task clarity | | | |
| Hierarchy | | | |
| Readability | | | |
| Responsive behavior | | | |
| Interaction clarity | | | |
| Product consistency | | | |
| Main tradeoff | | | |

Choose the candidate that best serves the target user and acceptance criteria. Do not select solely because it looks more novel.
