# Fresh Runner Contract

`loop/loop.sh` is a Bash coordinator for macOS, Linux, and compatible Unix-like environments. It launches exactly one adapter process, waits for it to finish, records its output, checks stop state, and only then starts another process.

## Adapter interface

Set `GODOT_DEV_RUNNER` to `claude`, `codex`, or an executable path. A custom executable receives:

```text
argv[1] = absolute target-project root
argv[2] = absolute loop/ITERATION_PROMPT.md path
```

It must start exactly one fresh non-interactive agent task using that prompt, wait for completion, and return the task's exit status. It must not reconnect to any previous thread, conversation, or session. The adapter may inherit the user's ordinary model, permission, sandbox, and tool configuration; it must not silently broaden them.

The loop never evaluates a shell command string. Relative custom paths resolve from the project root and are invoked as quoted argv.

## Built-in adapters

The Claude Code adapter uses current print mode and disables session persistence:

```text
claude --print --no-session-persistence <prompt-as-one-argv>
```

It never passes `--continue`, `--resume`, `--fork-session`, or `--session-id`.

The Codex adapter uses the documented non-interactive command and reads the prompt from stdin:

```text
codex exec -C <project-root> -
```

It never calls `codex exec resume`, `codex resume`, or supplies an earlier identifier. It does not hard-code sandbox, approval, full-access, or bypass flags.

Use `CLAUDE_BIN` or `CODEX_BIN` to select an explicit executable. Each adapter fails with a clear diagnostic when its CLI is missing.

## Loop controls

- `GODOT_DEV_MAX_ITERATIONS=0` — no numeric limit; STOP or BLOCKED controls completion. Any positive integer limits launches for that invocation.
- `GODOT_DEV_MAX_RUNNER_FAILURES=3` — consecutive nonzero adapter exits before the loop writes BLOCKED and stops.
- `GODOT_DEV_ITERATION_DELAY_SECONDS=2` — delay after an iteration when no terminal marker exists.

The loop validates these as non-negative integers. A successful runner exit resets the consecutive-failure counter. A maximum-iteration stop is a safety pause, not proof that DESIGN criteria are met, so it does not create STOP.

## Terminal behavior

Before the first launch and after every exit, the loop checks:

- `loop/STOP` — print its reason and exit successfully;
- `loop/BLOCKED` — print its reason and exit nonzero;
- required canonical state and prompt files; and
- the DESIGN required-section and unresolved-placeholder validator.

Repeated runner failure writes a human-readable BLOCKED reason. This prevents an uncontrolled hot loop even when the user intentionally leaves the numeric iteration limit unbounded.
