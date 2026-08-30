# Godot 4.x Visual QA Contract

V1 uses one engine adapter: Godot 4.x. Other engines require a future adapter and must not be represented as supported.

## One capture operation

`GAME_START=<state> ./scripts/game-capture.sh` performs:

1. project and graphical-session checks;
2. Godot executable discovery and a major-version check;
3. deterministic GAME_START resolution;
4. at most one explicit `--import` pass;
5. a separate normal Godot run of the isolated capture scene without `--headless`;
6. rendered-frame synchronization;
7. root Viewport image capture and PNG save;
8. JSON sidecar save; and
9. automatic process exit.

The import pass may use `--headless`; the rendered capture pass must not. Godot documents that `--headless` disables rendering and window management, so it cannot satisfy this workflow's visual gate.

## Executable and display checks

Set `GODOT_BIN` to an explicit executable when needed. Otherwise the script conservatively tries `godot4`, `godot`, `godot4.exe`, and `godot.exe`, plus the documented macOS application-bundle locations. It runs `--version` and requires major version 4. It never downloads or installs Godot.

On Linux and similar Unix sessions, either `DISPLAY` or `WAYLAND_DISPLAY` must be set. Absence is a blocker. Do not introduce a virtual display or silently switch to headless mode in v1.

## Deterministic state entry

`qa/visual-qa/godot/states.json` is a project-owned object mapping human-readable aliases to explicit `res://` scene paths:

```json
{
  "smoke": "res://qa/visual-qa/godot/smoke_state.tscn",
  "dungeon": "res://scenes/dungeon.tscn"
}
```

The resolver accepts a registered alias or a direct `res://...` scene path. It rejects unknown aliases, traversal, tabs/newlines, non-scene paths, and missing files. There is no fallback to the main scene or another alias.

V1 covers named scene/test-state entry and a single PNG. Scripted input sequences, game-playing automation, video, computer-vision scoring, and pixel-diff scoring are non-goals.

## Capture timing and failures

The isolated harness instantiates the resolved scene under its own root, allows initialization frames, then awaits `RenderingServer.frame_post_draw` before reading `get_viewport().get_texture().get_image()`. This prevents the common black or stale capture caused by reading the Viewport in `_ready()` too early.

The harness treats an empty image, a non-`OK` `save_png()` result, sidecar-open failure, or absent output as failure. It reports the requested state, resolved scene, and output path, then exits automatically with a success or failure code.

## Evidence judgment

The PNG and JSON sidecar prove capture mechanics, not visual quality. The current agent must open and inspect the newly generated PNG with a real local-image capability before recording visual success. Review the visible composition, readability, clipping, overlap, camera framing, missing assets, incorrect state, and material regressions related to the current work.

If no such capability exists, functional checks may still be reported separately, but any visual acceptance criterion remains BLOCKED.

## Optional live smoke test

Repository tests exercise generation, resolution, shell control flow, and stubbed Godot argv without requiring Godot or a display. In a real game project, visual readiness additionally requires:

```bash
GAME_START=smoke ./scripts/game-capture.sh
```

Inspect the resulting PNG before replacing or extending the smoke alias with game-owned states.
