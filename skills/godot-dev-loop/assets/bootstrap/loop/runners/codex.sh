#!/usr/bin/env bash
set -euo pipefail

if [[ "$#" -ne 2 ]]; then
  printf 'usage: %s <project-root> <prompt-file>\n' "$0" >&2
  exit 64
fi

PROJECT_ROOT="$(cd -- "$1" && pwd -P)"
PROMPT_FILE="$2"
CODEX_COMMAND="${CODEX_BIN:-codex}"

if ! command -v "$CODEX_COMMAND" >/dev/null 2>&1; then
  printf 'godot-dev-loop: Codex executable not found: %s\n' "$CODEX_COMMAND" >&2
  exit 127
fi
if [[ ! -f "$PROMPT_FILE" ]]; then
  printf 'godot-dev-loop: iteration prompt not found: %s\n' "$PROMPT_FILE" >&2
  exit 66
fi

cd -- "$PROJECT_ROOT"
exec "$CODEX_COMMAND" exec -C "$PROJECT_ROOT" - < "$PROMPT_FILE"
