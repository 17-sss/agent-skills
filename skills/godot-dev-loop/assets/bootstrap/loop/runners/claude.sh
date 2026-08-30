#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  printf 'usage: %s <project-root> <prompt-file>\n' "$0" >&2
  exit 64
fi

PROJECT_ROOT="$(cd -- "$1" && pwd -P)"
PROMPT_FILE="$2"
CLAUDE_COMMAND="${CLAUDE_BIN:-claude}"

if ! command -v "$CLAUDE_COMMAND" >/dev/null 2>&1; then
  printf 'godot-dev-loop: Claude Code executable not found: %s\n' "$CLAUDE_COMMAND" >&2
  exit 127
fi
if [[ ! -f "$PROMPT_FILE" ]]; then
  printf 'godot-dev-loop: iteration prompt not found: %s\n' "$PROMPT_FILE" >&2
  exit 66
fi

PROMPT="$(<"$PROMPT_FILE")"
cd -- "$PROJECT_ROOT"
exec "$CLAUDE_COMMAND" --print --no-session-persistence "$PROMPT"
