# Project State Contract

Use these files as the only canonical cross-iteration memory. Read them in this order every time:

1. `docs/feedback/INBOX.md` — latest human override
2. `docs/DESIGN.md` — durable product contract
3. `docs/STATUS.md` — current execution state

Conversation history is not authoritative.

## DESIGN.md

Keep this relatively stable and execution-ready. It must answer at least:

- what game is being built;
- what the player repeatedly does;
- what the current playable slice includes; and
- what observable condition means iteration should stop.

Normally include game concept, player fantasy or intended experience, core gameplay loop, playable-slice target, known visual direction, constraints, non-goals, good-enough criteria, and material user decisions.

Do not leave `TODO`, `TBD`, `???`, `[fill ...]`, `<answer ...>`, or equivalent unresolved required placeholders. Update DESIGN when a human directive intentionally changes the durable contract, and record that disposition in STATUS.

## STATUS.md

Keep STATUS compact enough to understand in under a minute. It is current truth, not an append-only log. Refresh it at the end of every successful material iteration and before writing STOP or BLOCKED.

Use these sections:

- `Current State` — what currently works and is playable;
- `Latest Evidence` — recent functional checks, captured GAME_START, PNG and sidecar paths, and whether the PNG was actually inspected;
- `Current Problems` — material known defects in scope;
- `Next Queue` — ordered, actionable work for the next fresh process;
- `Feedback Disposition` — active INBOX items marked implemented, pending, superseded, or blocked without deleting the human text;
- `Completed` — concise capabilities, not session narration; and
- `Blockers / Risks` — unresolved issues that materially affect continuation.

Replace stale statements when truth changes. Git history preserves chronology; STATUS preserves resumability.

## feedback/INBOX.md

Treat this file as user-owned and read-mostly. Human directives have precedence over stale STATUS entries but do not silently override the durable DESIGN contract.

- Do not casually rewrite, reorder, or delete directives.
- When a directive is satisfied, record the disposition in STATUS instead of removing it.
- When directives conflict, preserve them and request the smallest material user decision.
- When a directive changes product intent, update DESIGN explicitly during the same bounded iteration.

## STOP and BLOCKED

`loop/STOP` means every current DESIGN good-enough criterion is met. Its body is a short human-readable completion reason.

`loop/BLOCKED` means autonomous progress cannot safely continue. Examples include missing Godot 4.x, no graphical session, missing image inspection, repeated capture failure, an unresolved product choice, or the same technical blocker recurring without a new hypothesis.

Both files stop `loop/loop.sh`. Do not use STOP to hide incomplete criteria or BLOCKED as a substitute for ordinary debugging.
