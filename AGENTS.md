# AGENTS.md

This repository is a catalog of reusable agent skills. The repository root is not a skill package; actual skills live under `skills/`.

## Repository Overview

- `skills/` contains one directory per skill
- Each skill should be self-contained and installable on its own
- Root documentation should describe the catalog, not duplicate skill internals

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
- Keep root-level files generic to the collection
- Put install or agent-specific details in the skill package, not the repo root
- Prefer adding helper scripts and references over bloating `SKILL.md`
- Keep shared mutable project data in the target repository, not inside agent-specific config folders by default

## Updating an Existing Skill

- Preserve the skill directory name once published
- Update `README.md`, `SKILL.md`, and `metadata.json` together when the skill contract changes
- Keep examples and references aligned with the actual script behavior
- Validate the skill after structural changes
