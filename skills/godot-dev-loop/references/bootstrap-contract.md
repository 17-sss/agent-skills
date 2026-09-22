# Godot Loop Bootstrap

Read when the target project lacks the generated loop and QA files, or when bootstrap reports a conflict.

## Bootstrap a target Godot project

Confirm the target contains `project.godot`, then run the bundled helper from the installed skill directory:

```bash
python3 scripts/bootstrap_godot_dev_loop.py /path/to/game \
  --game "<game concept>" \
  --core-loop "<repeatable player loop>" \
  --good-enough "<observable stop condition>"
```

Optional arguments record player fantasy, playable-slice target, visual direction, constraints, and non-goals. If a complete canonical `docs/DESIGN.md` already exists, inspect it and use `--accept-existing-design`; the helper preserves it and validates the required sections.

The helper:

- checks `git rev-parse --show-toplevel` before considering `git init`;
- reuses an enclosing worktree instead of creating a nested repository;
- initializes Git only when the project is genuinely outside any repository;
- creates missing workflow, runner, state, and Godot QA files without silently overwriting existing files;
- leaves the real project main scene unchanged; and
- adds only a marked ignore block for transient captures, loop logs, STOP, and BLOCKED.

Resolve reported conflicts deliberately. Do not bypass them by deleting target-project files.
