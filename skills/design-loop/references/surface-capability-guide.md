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

## Optional Chromium Bootstrap

Use this only when no built-in browser, existing repository automation, browser MCP, Computer Use path, or user-provided capture can satisfy the required rendered evidence.

1. Explain that the fallback needs a network download, disk space, and a browser cache. Show the intended cache location and ask for explicit approval unless the user already authorized renderer installation.
2. Keep the runner and browser outside the target repository. Use a task-scoped temporary directory by default or a user-approved cache location. Redirect transient package-manager caches as well as `PLAYWRIGHT_BROWSERS_PATH` when Playwright is the selected runner.
3. Install Chromium only. Use the same explicit Playwright version for the browser download and the capture run.
4. Do not change project manifests, lockfiles, or `node_modules`. Do not install Chrome, Edge, Firefox, or WebKit as part of this fallback.
5. Do not run `install-deps`, `--with-deps`, `sudo`, or an operating-system package manager without separate explicit authorization for that exact host change.
6. Capture one disposable smoke screenshot before relying on the bootstrap. If launch fails because system libraries are missing, report the missing dependency and stop instead of escalating silently.
7. Remove task-scoped downloads after use. If the user approved a persistent cache, report its location so it can be reused or removed intentionally.

Renderer bootstrap is a recovery path, not a package dependency. Do not install anything when an existing capability already provides equivalent evidence.

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
