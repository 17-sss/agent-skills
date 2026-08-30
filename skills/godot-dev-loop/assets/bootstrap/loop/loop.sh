#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
PROMPT_FILE="$SCRIPT_DIR/ITERATION_PROMPT.md"
STOP_FILE="$SCRIPT_DIR/STOP"
BLOCKED_FILE="$SCRIPT_DIR/BLOCKED"
LOG_DIR="$SCRIPT_DIR/logs"

MAX_ITERATIONS="${GODOT_DEV_MAX_ITERATIONS:-0}"
MAX_FAILURES="${GODOT_DEV_MAX_RUNNER_FAILURES:-3}"
DELAY_SECONDS="${GODOT_DEV_ITERATION_DELAY_SECONDS:-2}"

require_non_negative_integer() {
  local name="$1"
  local value="$2"
  if [[ ! "$value" =~ ^[0-9]+$ ]]; then
    printf 'godot-dev-loop: %s must be a non-negative integer, got %q\n' "$name" "$value" >&2
    exit 64
  fi
}

write_blocked() {
  local reason="$1"
  printf '%s\n' "$reason" > "$BLOCKED_FILE"
  printf 'godot-dev-loop: BLOCKED: %s\n' "$reason" >&2
}

stop_if_terminal() {
  if [[ -f "$STOP_FILE" ]]; then
    printf 'godot-dev-loop: STOP: '
    sed -n '1p' "$STOP_FILE"
    exit 0
  fi
  if [[ -f "$BLOCKED_FILE" ]]; then
    printf 'godot-dev-loop: BLOCKED: ' >&2
    sed -n '1p' "$BLOCKED_FILE" >&2
    exit 2
  fi
}

require_non_negative_integer GODOT_DEV_MAX_ITERATIONS "$MAX_ITERATIONS"
require_non_negative_integer GODOT_DEV_MAX_RUNNER_FAILURES "$MAX_FAILURES"
require_non_negative_integer GODOT_DEV_ITERATION_DELAY_SECONDS "$DELAY_SECONDS"
if [[ "$MAX_FAILURES" == "0" ]]; then
  printf 'godot-dev-loop: GODOT_DEV_MAX_RUNNER_FAILURES must be at least 1\n' >&2
  exit 64
fi

stop_if_terminal

for required in \
  "$PROJECT_ROOT/docs/feedback/INBOX.md" \
  "$PROJECT_ROOT/docs/DESIGN.md" \
  "$PROJECT_ROOT/docs/STATUS.md" \
  "$PROMPT_FILE"; do
  if [[ ! -f "$required" ]]; then
    write_blocked "Required durable state is missing: ${required#$PROJECT_ROOT/}"
    exit 2
  fi
done

if ! design_error="$(python3 "$PROJECT_ROOT/scripts/validate-game-design.py" "$PROJECT_ROOT/docs/DESIGN.md" 2>&1)"; then
  write_blocked "DESIGN validation failed: $design_error"
  exit 2
fi

RUNNER="${GODOT_DEV_RUNNER:-}"
if [[ -z "$RUNNER" ]]; then
  write_blocked "Set GODOT_DEV_RUNNER to claude, codex, or an executable adapter path."
  exit 2
fi

case "$RUNNER" in
  claude)
    ADAPTER="$SCRIPT_DIR/runners/claude.sh"
    ;;
  codex)
    ADAPTER="$SCRIPT_DIR/runners/codex.sh"
    ;;
  *)
    if [[ "$RUNNER" == /* ]]; then
      ADAPTER="$RUNNER"
    else
      ADAPTER="$PROJECT_ROOT/$RUNNER"
    fi
    ;;
esac

if [[ ! -x "$ADAPTER" ]]; then
  write_blocked "Runner adapter is missing or not executable: $ADAPTER"
  exit 2
fi

mkdir -p "$LOG_DIR"
iteration=0
consecutive_failures=0

while true; do
  stop_if_terminal
  if (( MAX_ITERATIONS > 0 && iteration >= MAX_ITERATIONS )); then
    printf 'godot-dev-loop: reached GODOT_DEV_MAX_ITERATIONS=%s without STOP or BLOCKED\n' "$MAX_ITERATIONS"
    exit 0
  fi

  iteration=$((iteration + 1))
  printf -v iteration_label '%06d' "$iteration"
  log_file="$LOG_DIR/iteration-$iteration_label.log"
  printf 'godot-dev-loop: starting fresh iteration %s with %s\n' "$iteration" "$RUNNER"

  if "$ADAPTER" "$PROJECT_ROOT" "$PROMPT_FILE" 2>&1 | tee "$log_file"; then
    consecutive_failures=0
  else
    runner_status=$?
    consecutive_failures=$((consecutive_failures + 1))
    printf 'godot-dev-loop: runner exited %s (%s/%s consecutive failures)\n' \
      "$runner_status" "$consecutive_failures" "$MAX_FAILURES" >&2
  fi

  stop_if_terminal

  if (( consecutive_failures >= MAX_FAILURES )); then
    write_blocked "Runner failed $consecutive_failures consecutive times; inspect $log_file before retrying."
    exit 2
  fi

  if (( DELAY_SECONDS > 0 )); then
    sleep "$DELAY_SECONDS"
  fi
done
