# Status

## Current State

- The durable game-development workflow is bootstrapped.
- Visual QA is not ready until the smoke capture opens a real window, writes a PNG, and an image-capable agent inspects it.

## Latest Evidence

- Functional: bootstrap completed; no game-specific check recorded yet.
- Visual: no inspected capture recorded yet.

## Current Problems

- Real-window Godot capture and local image inspection remain unverified.

## Next Queue

1. Run `GAME_START=smoke ./scripts/game-capture.sh` in a graphical session.
2. Inspect the new PNG and record the PNG and JSON sidecar paths here.
3. Register the first game-owned state in `qa/visual-qa/godot/states.json`.
4. Choose one bounded playable-slice improvement from `docs/DESIGN.md`.

## Feedback Disposition

- No human directive has been dispositioned yet. Preserve `docs/feedback/INBOX.md` as user-owned input.

## Completed

- Canonical design, status, feedback, capture, and fresh-runner paths established.

## Blockers / Risks

- Do not launch autonomous iterations until visual observability and image inspection are proven.
