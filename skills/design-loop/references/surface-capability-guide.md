# Surface Capability Guide

Choose capabilities by what the task needs, not by assuming a fixed tool name. Agent apps, CLIs, IDEs, and plugin installations can expose different tools.

## Capability Selection

| Need | Preferred path | Fallback |
| --- | --- | --- |
| Run the product | Repository dev or preview command | Smallest supported static preview |
| Inspect localhost | Built-in browser or browser automation | User-provided screenshot from the running product |
| Capture viewports | Browser screenshot at explicit dimensions | OS screenshot with viewport dimensions recorded |
| Test interactions | Browser automation or Computer Use | Existing end-to-end tests, then a clearly reported manual gap |
| Inspect an image | Native image input or local image viewer | Pass the screenshot to a fresh inspection turn as an image input |
| Generate a raster asset | Image-generation tool or `$imagegen` | Use a temporary placeholder and report the missing capability |

Do not call a capability "Vision" as though it were always a separate tool. The important action is to load and inspect actual rendered pixels.

## App or Desktop

- Prefer the built-in browser for localhost when it is available.
- Use browser interaction or Computer Use for click, keyboard, hover, and responsive checks.
- Capture screenshots at explicit desktop and mobile dimensions.
- Use the local image viewer for screenshots already written to disk.
- Use image generation only when the task needs a new raster asset.

## CLI or IDE

- Start the application from the terminal and keep the process available during the review loop.
- Prefer an existing Playwright setup, browser MCP server, or repository screenshot command.
- Do not add a browser dependency when the repository already has an equivalent tool.
- When a CLI accepts local image inputs, pass the screenshot directly. For example, Codex CLI supports:

  ```bash
  codex --image before.png,after.png "Compare these rendered states and identify regressions."
  ```

- If the current session cannot load images, save the screenshot and report the exact verification gap instead of pretending to have inspected it.

## Default Viewports

When the product has no documented device matrix, start with:

- desktop: `1440 x 900`
- mobile: `390 x 844`

Add a compact tablet or narrow laptop viewport only when the layout has a relevant breakpoint or the user asks for it. Prefer repository-defined breakpoints over these defaults.

## Browser Evidence Rules

- Keep route, seed data, account state, viewport, and scroll position stable between comparisons.
- Capture important open states separately: menu open, dialog open, validation visible, loading, empty, and error.
- Record whether screenshots are baseline, candidate, or final.
- Store transient evidence in the repository's existing artifact path or a temporary directory. Do not commit screenshots by default.
- Inspect console and network failures when they can change the visual result.

## Image Generation Rules

Generate assets for cases such as a product illustration, game portrait, textured background, or unique raster placeholder. Do not generate:

- existing brand marks or imitations of third-party brands
- standard interface icons already available in the product's icon system
- assets better expressed as HTML, CSS, canvas, or SVG code
- decorative imagery that distracts from the primary task

After generation, place the asset in the real layout and re-run the screenshot review. An attractive asset in isolation can still harm hierarchy, contrast, performance, or responsiveness.
