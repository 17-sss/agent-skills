# AGENTS.md

This package defines the `design-loop` skill.

## Package Intent

- Turn UI implementation into a rendered evidence loop.
- Work across app, CLI, and IDE surfaces without hard-coding one tool name.
- Keep visual review, interaction testing, and code validation connected.
- Use image generation selectively rather than as a default styling step.
- Use Product Design only as an optional, availability-gated accelerator and return to the package's rendered evidence loop afterward.

## Editing Guidance

- Keep `SKILL.md`, `README.md`, `metadata.json`, and `agents/openai.yaml` aligned when the skill contract changes.
- Keep the skill focused on executable visual iteration. Do not absorb durable product-direction governance or strict pixel-matching workflows.
- Preserve audit-only behavior: review requests do not authorize code edits.
- Preserve the requirement for fresh rendered evidence before visual completion claims.
- Keep surface-specific details in `references/surface-capability-guide.md`.
- Keep review criteria in `references/visual-review-rubric.md`.
- Keep reusable invocation examples in `references/prompt-recipes.md`.
- Avoid adding scripts until a deterministic operation is repeated often enough to justify one.
- Do not add a mandatory MCP, plugin, browser, or image-generation dependency; capability fallback is part of the skill contract.
- Keep Product Design routing in `references/surface-capability-guide.md`; never make the core workflow depend on that plugin.
- Preserve the explicit-approval, repository-isolated Chromium fallback. Never turn it into an automatic install or system-package mutation.

## Validation

- Run the skill validator after structural or frontmatter changes.
- Parse `metadata.json` and `agents/openai.yaml` after edits.
- Check Markdown links and repository-relative references.
- Confirm root `README.md` still advertises the package accurately.
