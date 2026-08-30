#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"
QA_ROOT="$PROJECT_ROOT/qa/visual-qa/godot"
RESOLVER="$QA_ROOT/resolve_game_state.py"
HARNESS_SCENE="res://qa/visual-qa/godot/capture_harness.tscn"

if [[ ! -f "$PROJECT_ROOT/project.godot" ]]; then
  printf 'godot-dev-loop: project.godot not found under %s\n' "$PROJECT_ROOT" >&2
  exit 66
fi
if [[ -z "${GAME_START:-}" ]]; then
  printf 'godot-dev-loop: set GAME_START to a registered alias or res:// scene path\n' >&2
  exit 64
fi

case "$(uname -s)" in
  Linux*|FreeBSD*)
    if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
      printf 'godot-dev-loop: no DISPLAY or WAYLAND_DISPLAY; real-window visual QA is unavailable\n' >&2
      exit 3
    fi
    ;;
esac

resolve_executable() {
  local candidate="$1"
  if [[ "$candidate" == */* ]]; then
    [[ -x "$candidate" ]] && printf '%s\n' "$candidate"
  else
    command -v "$candidate" 2>/dev/null || true
  fi
}

godot_bin=""
if [[ -n "${GODOT_BIN:-}" ]]; then
  godot_bin="$(resolve_executable "$GODOT_BIN")"
else
  for candidate in \
    godot4 \
    godot \
    godot4.exe \
    godot.exe \
    /Applications/Godot.app/Contents/MacOS/Godot \
    "${HOME:-}/Applications/Godot.app/Contents/MacOS/Godot"; do
    godot_bin="$(resolve_executable "$candidate")"
    [[ -n "$godot_bin" ]] && break
  done
fi

if [[ -z "$godot_bin" ]]; then
  printf 'godot-dev-loop: Godot 4.x not found; set GODOT_BIN to the editor executable\n' >&2
  exit 127
fi

version_output="$("$godot_bin" --version 2>&1)"
godot_version="${version_output%%$'\n'*}"
if [[ ! "$godot_version" =~ ^4([.]|$) ]]; then
  printf 'godot-dev-loop: Godot 4.x is required, got %s from %s\n' "$godot_version" "$godot_bin" >&2
  exit 65
fi

state_info="$(python3 "$RESOLVER" --project-root "$PROJECT_ROOT" --state "$GAME_START")"
IFS=$'\t' read -r requested_state resolved_scene artifact_stem <<< "$state_info"
if [[ -z "$requested_state" || -z "$resolved_scene" || -z "$artifact_stem" ]]; then
  printf 'godot-dev-loop: state resolver returned incomplete output\n' >&2
  exit 70
fi

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
if [[ -n "${GAME_CAPTURE_OUTPUT:-}" ]]; then
  if [[ "$GAME_CAPTURE_OUTPUT" == /* || "$GAME_CAPTURE_OUTPUT" == *".."* ]]; then
    printf 'godot-dev-loop: GAME_CAPTURE_OUTPUT must be a project-relative path without ..\n' >&2
    exit 64
  fi
  capture_path="$PROJECT_ROOT/$GAME_CAPTURE_OUTPUT"
else
  capture_path="$PROJECT_ROOT/artifacts/visual/$timestamp-$artifact_stem-${BASHPID}.png"
fi
capture_metadata="$capture_path.json"
mkdir -p "$(dirname -- "$capture_path")"
if [[ -e "$capture_path" || -e "$capture_metadata" ]]; then
  printf 'godot-dev-loop: refusing to overwrite existing capture output: %s\n' "$capture_path" >&2
  exit 73
fi

printf 'godot-dev-loop: importing project with Godot %s\n' "$godot_version"
"$godot_bin" --headless --path "$PROJECT_ROOT" --import

printf 'godot-dev-loop: rendering state=%s scene=%s in a normal Godot window\n' \
  "$requested_state" "$resolved_scene"
GAME_START="$requested_state" \
GAME_RESOLVED_SCENE="$resolved_scene" \
GAME_CAPTURE_PATH="$capture_path" \
  "$godot_bin" --path "$PROJECT_ROOT" --scene "$HARNESS_SCENE"

if [[ ! -s "$capture_path" ]]; then
  printf 'godot-dev-loop: capture run returned without a non-empty PNG: %s\n' "$capture_path" >&2
  exit 74
fi
if [[ ! -s "$capture_metadata" ]]; then
  printf 'godot-dev-loop: capture run returned without metadata: %s\n' "$capture_metadata" >&2
  exit 74
fi

printf 'godot-dev-loop: PNG=%s\n' "$capture_path"
printf 'godot-dev-loop: metadata=%s\n' "$capture_metadata"
printf 'godot-dev-loop: open and inspect the PNG before recording visual success\n'
