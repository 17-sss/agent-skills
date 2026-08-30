# Godot Development Loop

`godot-dev-loop` is a standalone, cross-agent workflow for Godot 4.x projects. It combines a concise human game brief, repository-owned state, deterministic scene entry, real-window PNG capture, image inspection, and fresh non-interactive agent processes.

It is designed for playable-game work that may run for many iterations while each agent process remains disposable. It is not a generic infinite prompt loop and does not depend on another skill.

## What it installs into a game project

- `docs/DESIGN.md`, `docs/STATUS.md`, and `docs/feedback/INBOX.md`
- `scripts/game-capture.sh` and design validation
- an isolated Godot 4 capture scene, explicit state registry, and smoke state under `qa/visual-qa/godot/`
- `loop/ITERATION_PROMPT.md`, `loop/loop.sh`, and Claude Code/Codex runner adapters
- ignored project-local visual artifacts and loop logs

The bootstrap helper preserves existing state and QA files. It never changes the project's real main scene and never creates a nested Git repository.

## Bootstrap

From the installed skill directory:

```bash
python3 scripts/bootstrap_godot_dev_loop.py /path/to/game \
  --game "A compact tactical dungeon crawler" \
  --core-loop "Explore, choose a fight, resolve it, and improve the party" \
  --good-enough "The smoke and dungeon states render, one encounter is winnable, and no blocking visual defect remains"
```

Then prove the real-window visual path and inspect the resulting PNG:

```bash
cd /path/to/game
GAME_START=smoke ./scripts/game-capture.sh
```

Set `GODOT_BIN` when Godot is not discoverable as `godot4`, `godot`, `godot4.exe`, or `godot.exe`. The helper does not download Godot.

## Run fresh iterations

Select an adapter explicitly:

```bash
GODOT_DEV_RUNNER=codex ./loop/loop.sh
GODOT_DEV_RUNNER=claude ./loop/loop.sh
GODOT_DEV_RUNNER=./path/to/custom-adapter ./loop/loop.sh
```

The custom adapter receives exactly two arguments: the absolute project root and the absolute iteration-prompt path. It must start one fresh non-interactive agent process, wait for it, and return that process's exit status.

The loop is Bash for macOS, Linux, and compatible Unix-like environments. `GODOT_DEV_MAX_ITERATIONS=0` means run until STOP or BLOCKED. `GODOT_DEV_MAX_RUNNER_FAILURES`, default `3`, prevents a failing runner from becoming a hot loop; `GODOT_DEV_ITERATION_DELAY_SECONDS`, default `2`, controls the delay.

Read [SKILL.md](SKILL.md) for the executable workflow and the files under [references](references/project-state-contract.md) for the durable-state, Godot QA, and runner contracts.
