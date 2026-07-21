# Design Loop

Reusable agent workflow for building and improving interfaces through rendered visual feedback rather than stopping after the first code pass.

## Why This Is a Skill

This workflow is reusable instruction, so a skill is the smallest appropriate agent extension:

- A note file requires copying the full prompt into every task.
- `AGENTS.md` would apply the workflow to every task in a repository, including non-visual work.
- A hook is appropriate for lifecycle enforcement, not an opt-in design workflow.
- A plugin becomes useful later if this workflow must ship with browser tooling, an MCP server, hooks, or multiple related skills.

The skill prefers capabilities already present in the current app, CLI, IDE, or repository. It does not require a plugin, MCP server, or bundled browser dependency. When no renderer exists, it may offer an explicit, isolated Chromium bootstrap before reporting the visual-verification gap.

## Use When

- Building a new UI, frontend screen, product flow, dashboard, admin page, landing page, or game interface
- Polishing an existing implementation beyond its first draft
- Checking desktop and mobile rendered states
- Testing visible interaction states and primary user flows
- Comparing two or three visual alternatives
- Integrating a generated raster asset and reviewing it in context
- Extracting reusable design rules from a successful implementation

## Core Loop

1. Inspect the repository and existing design contract.
2. Run the product and capture a baseline.
3. Build a coherent functional pass.
4. Review real desktop and mobile screenshots.
5. Exercise the primary interaction flow.
6. Fix one issue cluster at a time and capture fresh evidence.
7. Verify code checks and report remaining gaps.

## Installation

Install this skill from the collection:

```bash
npx skills add https://github.com/17-sss/agent-skills --skill design-loop
```

Or copy `skills/design-loop` to a supported global or project skill directory.

## Usage

Explicit invocation:

```text
Use $design-loop to improve the checkout screen. Preserve behavior,
verify desktop and mobile renders, test the primary flow, and iterate on major visual issues.
```

An agent can also select the skill implicitly when a task matches its description.

See [prompt-recipes.md](references/prompt-recipes.md) for the full visual loop plus dedicated build, improvement, game UI, product UI, audit-only, variant, asset, and design-rule examples.

## Surface Support

- **App/Desktop surfaces:** use the built-in browser, computer-use tools, screenshot inspection, and image generation when available.
- **CLI/IDE surfaces:** use repository browser automation, Playwright or browser MCP when installed, and local image inputs.
- **No render-capable path:** offer a user-approved Chromium-only bootstrap that does not modify the target repository or install system packages. If it is declined or cannot launch, complete only separately valid non-visual work and report visual verification as a concrete gap.

Tool names vary by installation. The skill selects capabilities rather than depending on one fixed browser or screenshot integration.

## Related Workflows

- Use a design-source workflow when product direction and durable `DESIGN.md` guidance must be established first.
- Use a strict visual-reference workflow when pixel-level matching to an approved image or URL is the acceptance criterion.
- Use `imagegen` only when a new raster asset is part of the solution.
