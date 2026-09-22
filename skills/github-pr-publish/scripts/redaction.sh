#!/usr/bin/env bash
# Package-local, fail-closed command capture. Raw output stays in kernel pipes.

REDACTION_TEMP_DIRS=()
REDACTION_TEMP_FILES=()

sanitize_stream() {
  sed -E \
    -e 's/(Authorization[[:space:]]*:[[:space:]]*)(Bearer|Basic|token)[[:space:]]+\\"[^"]*\\"/\1[REDACTED]/Ig' \
    -e 's/(Authorization[[:space:]]*:[[:space:]]*)(Bearer|Basic|token)[[:space:]]+"[^"]*"/\1[REDACTED]/Ig' \
    -e "s/(Authorization[[:space:]]*:[[:space:]]*)(Bearer|Basic|token)[[:space:]]+'[^']*'/\\1[REDACTED]/Ig" \
    -e 's/(Authorization[[:space:]]*:[[:space:]]*)(Bearer|Basic|token)[[:space:]]+[^[:space:]",}]+/\1[REDACTED]/Ig' \
    -e 's/(Authorization[[:space:]]*:[[:space:]]*)[^[:space:]",}]+/\1[REDACTED]/Ig' \
    -e 's/(token|GH_TOKEN|GITHUB_TOKEN|PAT)=([^[:space:]",}]+)/\1=[REDACTED]/Ig' \
    -e 's#(https?://)[^/@[:space:]]+(:[^/@[:space:]]+)?@#\1[REDACTED]@#g' \
    -e 's/(github_pat_|gh[pousr]_)[A-Za-z0-9_]+/\1[REDACTED]/g'
}

redaction_cleanup() {
  local dir file
  for file in "${REDACTION_TEMP_FILES[@]}"; do
    rm -f -- "$file"
  done
  for dir in "${REDACTION_TEMP_DIRS[@]}"; do
    [[ -d "$dir" ]] && rm -rf -- "$dir"
  done
  return 0
}

trap redaction_cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

capture_command() {
  local out_file=$1 err_file=$2 fifo_dir command_status out_status err_status out_pid err_pid
  shift 2
  umask 077
  fifo_dir=$(mktemp -d "${TMPDIR:-/tmp}/pr-redaction.XXXXXX") || exit 125
  REDACTION_TEMP_DIRS+=("$fifo_dir")
  if ! mkfifo "$fifo_dir/out" "$fifo_dir/err"; then
    printf 'error: failed to prepare sanitized capture\n' >&2
    exit 125
  fi
  sanitize_stream <"$fifo_dir/out" >"$out_file" & out_pid=$!
  sanitize_stream <"$fifo_dir/err" >"$err_file" & err_pid=$!
  if "$@" >"$fifo_dir/out" 2>"$fifo_dir/err"; then command_status=0; else command_status=$?; fi
  if wait "$out_pid"; then out_status=0; else out_status=$?; fi
  if wait "$err_pid"; then err_status=0; else err_status=$?; fi
  rm -rf -- "$fifo_dir"
  if ((out_status != 0 || err_status != 0)); then
    rm -f -- "$out_file" "$err_file"
    printf 'error: output redaction failed\n' >&2
    exit 125
  fi
  return "$command_status"
}
