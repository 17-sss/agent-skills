# AGENTS.md

This package defines the `handoff-memory` skill.

## Package Intent

- Keep the shared mutable handoff file inside the target repository
- Support multiple agent environments without making any one agent folder the default data store
- Preserve one canonical HANDOFF file per repository

## Resolver Rules

- Honor `--handoff-path` when the caller gives one
- Otherwise prefer an existing shared handoff file in this order:
  - `docs/HANDOFF.md`
  - `memories/HANDOFF.md`
  - `HANDOFF.md`
- If none exists, create `docs/HANDOFF.md`

## Editing Guidance

- Keep `SKILL.md`, `README.md`, and `metadata.json` aligned
- Update the template if the expected HANDOFF sections change
- Do not reintroduce global machine-local storage as the default behavior
