# AGENTS.md

This repository is a catalog of reusable agent skills. The repository root is not a skill package; actual skills live under `skills/`.

## Repository Overview

- `skills/` contains one directory per skill
- Each skill should be self-contained and installable on its own
- Root documentation should describe the catalog, not duplicate skill internals
- `README.md` is the default English catalog and `README.ko.md` is its Korean counterpart; keep their skill inventory, grouping, usage examples, and maintenance commands aligned
- `.claude-plugin/marketplace.json` is compatibility metadata used by the `skills` CLI to group the six Codex-native workflows under `Codex` and the cross-agent skills under `Other`
- Keep the grouping manifest aligned with the Codex-native inventory without introducing Claude Code runtime dependencies into the skills

## Creating a New Skill

Use this structure:

```text
skills/
  {skill-name}/
    SKILL.md
    README.md
    AGENTS.md
    metadata.json
    scripts/
    references/
    agents/
```

Rules:

- Use kebab-case for skill directory names
- `README.md` and package-local `AGENTS.md` are optional when they would only duplicate `SKILL.md` or repository-wide guidance
- Keep root-level files generic to the collection
- Put install or agent-specific details in the skill package, not the repo root
- Prefer adding helper scripts and references over bloating `SKILL.md`
- Keep shared mutable project data in the target repository, not inside agent-specific config folders by default

## Updating an Existing Skill

- Preserve the skill directory name once published
- Update `SKILL.md`, `metadata.json`, and any existing package `README.md` together when the skill contract changes
- Keep examples and references aligned with the actual script behavior
- When either inventory changes, update `.claude-plugin/marketplace.json`, the root catalog, and the grouping contract tests together
- Validate the skill after structural changes
