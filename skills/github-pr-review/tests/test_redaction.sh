#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SKILL_DIR=$(cd "$SCRIPT_DIR/.." && pwd)
TEST_TMP=$(mktemp -d "${TMPDIR:-/tmp}/github-pr-review-tests.XXXXXX")
trap 'rm -rf "$TEST_TMP"' EXIT

export PATH="$SCRIPT_DIR/fake-bin:$PATH"
export FAKE_SECRET_TOKEN='redaction-env-should-not-leak'
export FAKE_GH_LOG="$TEST_TMP/gh.log"
: >"$FAKE_GH_LOG"
reviewed_sha=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

assert_not_contains() {
  local file=$1 pattern=$2
  if grep -qF "$pattern" "$file"; then
    printf 'not ok - %s still contains %s\n' "$file" "$pattern" >&2
    cat "$file" >&2
    exit 1
  fi
}

assert_contains() {
  local file=$1 pattern=$2
  if ! grep -qF "$pattern" "$file"; then
    printf 'not ok - %s missing %s\n' "$file" "$pattern" >&2
    cat "$file" >&2
    exit 1
  fi
}

assert_private_tree() {
  python3 - "$1" <<'PY'
import os
import stat
import sys
from pathlib import Path

root = Path(sys.argv[1])
paths = [root] + [path for path in root.rglob("*") if path.exists()]
for path in paths:
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise SystemExit(f"{path} is not private: {oct(mode)}")
PY
}

body="$TEST_TMP/review.md"
printf 'review body\n' > "$body"

post_out="$TEST_TMP/post.out"
post_err="$TEST_TMP/post.err"
if bash "$SKILL_DIR/scripts/post_review.sh" OWNER/REPO#1 "$body" --commit-sha "$reviewed_sha" >"$post_out" 2>"$post_err"; then
  printf 'not ok - post_review should fail under fake gh\n' >&2
  exit 1
fi
assert_not_contains "$post_err" "$FAKE_SECRET_TOKEN"
assert_not_contains "$post_err" 'Authorization: token='
assert_contains "$post_err" '[REDACTED]'
printf 'ok 1 - post_review redacts failing gh stderr\n'

collect_dir="$TEST_TMP/context"
collect_out="$TEST_TMP/collect.out"
collect_err="$TEST_TMP/collect.err"
if bash "$SKILL_DIR/scripts/collect_pr_context.sh" OWNER/REPO#1 --output-dir "$collect_dir" >"$collect_out" 2>"$collect_err"; then
  printf 'not ok - collect_pr_context should fail under fake gh\n' >&2
  exit 1
fi
for file in "$collect_dir"/* "$collect_err"; do
  [[ -f "$file" ]] || continue
  assert_not_contains "$file" "$FAKE_SECRET_TOKEN"
  assert_not_contains "$file" 'Authorization: token='
  assert_not_contains "$file" 'x-access-token:'
done
assert_contains "$collect_dir/pr-view.err" '[REDACTED]'
printf 'ok 2 - collect_pr_context redacts saved gh stderr\n'

assert_private_tree "$collect_dir"
printf 'ok 3 - collect_pr_context keeps output permissions private\n'

: >"$FAKE_GH_LOG"
export FAKE_INACTIVE_AUTH_FAIL=1
export FAKE_REVIEW_SUCCEED=1
active_out="$TEST_TMP/active.out"
active_err="$TEST_TMP/active.err"
bash "$SKILL_DIR/scripts/post_review.sh" OWNER/REPO#1 "$body" --commit-sha "$reviewed_sha" >"$active_out" 2>"$active_err"
assert_contains "$FAKE_GH_LOG" 'auth status --active --hostname github.com'
assert_contains "$FAKE_GH_LOG" 'pr view 1 --repo OWNER/REPO --json headRefOid --jq .headRefOid'
assert_contains "$FAKE_GH_LOG" 'pr review 1 --repo OWNER/REPO --comment'
printf 'ok 4 - posting uses the active identity and verifies the reviewed head\n'

: >"$FAKE_GH_LOG"
export FAKE_HEAD_SHA=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb
drift_out="$TEST_TMP/drift.out"
drift_err="$TEST_TMP/drift.err"
if bash "$SKILL_DIR/scripts/post_review.sh" OWNER/REPO#1 "$body" --commit-sha "$reviewed_sha" >"$drift_out" 2>"$drift_err"; then
  printf 'not ok - post_review should stop after PR head drift\n' >&2
  exit 1
fi
assert_contains "$drift_err" 'PR head moved from reviewed SHA'
if grep -F 'pr review' "$FAKE_GH_LOG" >/dev/null; then
  printf 'not ok - post_review mutated GitHub after detecting head drift\n' >&2
  cat "$FAKE_GH_LOG" >&2
  exit 1
fi
printf 'ok 5 - posting stops when the PR head moves\n'

cat >"$TEST_TMP/emit-credentials.sh" <<'EOF'
printf '%s\n' '{"message":"aUtHoRiZaTiOn :  bAsIc   fake-json-secret","quoted":"Authorization: Basic \"fake-json-quoted-secret\"","ok":true}'
printf '%s\n' 'Authorization: Bearer fake-bearer-secret' 'AUTHORIZATION: token fake-token-secret' 'Authorization: Bearer "fake-double-secret"' "Authorization: Basic 'fake-single-secret'" 'GH_TOKEN=fake-env-secret' 'https://x-access-token:fake-url-secret@github.com/OWNER/REPO' 'http://user:fake-http-secret@github.com/OWNER/REPO' 'github_pat_fakeprefixsecret' >&2
exit 17
EOF
safe_out="$TEST_TMP/safe.json"
safe_err="$TEST_TMP/safe.err"
if bash -c 'source "$1"; capture_command "$2" "$3" bash "$4"' _ "$SKILL_DIR/scripts/redaction.sh" "$safe_out" "$safe_err" "$TEST_TMP/emit-credentials.sh"; then
  printf 'not ok - capture must preserve command failure\n' >&2
  exit 1
else
  [[ $? -eq 17 ]] || { printf 'not ok - capture changed command failure code\n' >&2; exit 1; }
fi
for secret in fake-json-secret fake-json-quoted-secret fake-bearer-secret fake-token-secret fake-double-secret fake-single-secret fake-env-secret fake-url-secret fake-http-secret fakeprefixsecret; do
  assert_not_contains "$safe_out" "$secret"
  assert_not_contains "$safe_err" "$secret"
done
python3 -m json.tool "$safe_out" >/dev/null
assert_contains "$safe_err" '[REDACTED]'
assert_contains "$safe_err" 'http://[REDACTED]@github.com/OWNER/REPO'
printf 'ok 6 - capture redacts mixed headers and preserves JSON and exit status\n'

mkdir "$TEST_TMP/fail-bin"
printf '#!/usr/bin/env bash\nexit 31\n' >"$TEST_TMP/fail-bin/sed"
chmod +x "$TEST_TMP/fail-bin/sed"
if PATH="$TEST_TMP/fail-bin:$PATH" bash -c 'source "$1"; capture_command "$2" "$3" bash "$4"' _ "$SKILL_DIR/scripts/redaction.sh" "$TEST_TMP/failed.out" "$TEST_TMP/failed.err" "$TEST_TMP/emit-credentials.sh" >"$TEST_TMP/failed.log" 2>&1; then
  printf 'not ok - failed redaction must stop capture\n' >&2
  exit 1
fi
[[ ! -e "$TEST_TMP/failed.out" && ! -e "$TEST_TMP/failed.err" ]] || { printf 'not ok - failed redaction left output files\n' >&2; exit 1; }
assert_not_contains "$TEST_TMP/failed.log" fake-bearer-secret
printf 'ok 7 - failed redaction leaves no raw output\n'

if command -v timeout >/dev/null 2>&1; then
  cat >"$TEST_TMP/interrupt-credentials.sh" <<'EOF'
printf '%s\n' 'Authorization: Bearer fake-interrupt-secret'
sleep 5
EOF
  if TMPDIR="$TEST_TMP" timeout --kill-after=2s -s TERM 1s bash -c \
    'source "$1"; capture_command "$2" "$3" bash "$4"' _ \
    "$SKILL_DIR/scripts/redaction.sh" "$TEST_TMP/interrupted.out" \
    "$TEST_TMP/interrupted.err" "$TEST_TMP/interrupt-credentials.sh" \
    >"$TEST_TMP/interrupted.log" 2>&1; then
    printf 'not ok - interrupted capture unexpectedly succeeded\n' >&2
    exit 1
  fi
  if find "$TEST_TMP" -maxdepth 1 -name 'pr-redaction.*' | grep -q .; then
    printf 'not ok - interrupted capture left a FIFO directory\n' >&2
    exit 1
  fi
  for file in "$TEST_TMP/interrupted.out" "$TEST_TMP/interrupted.err" "$TEST_TMP/interrupted.log"; do
    [[ -f "$file" ]] && assert_not_contains "$file" fake-interrupt-secret
  done
  printf 'ok 8 - interrupted capture cleans FIFOs and does not expose raw output\n'
fi

printf 'All github-pr-review redaction tests passed\n'
