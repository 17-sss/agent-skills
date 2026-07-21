#!/usr/bin/env python3
"""Manage standalone repository-local state for milestone-runner."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
import ctypes
from datetime import datetime, timezone
import errno
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import sys
from typing import Any, Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows falls back to revision checks.
    fcntl = None


STATE_DIRECTORY = ".agent-workflows"
TRANSACTION_FILE = ".pending-transaction.json"
SCHEMA_VERSION = 1
SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
GOAL_ID_PATTERN = re.compile(r"G[0-9]{3,}")
GOAL_STATUSES = {"pending", "in_progress", "complete", "blocked", "superseded"}
TERMINAL_GOAL_STATUSES = {"complete", "superseded"}
PLAN_STATUSES = {"active", "blocked", "complete"}


class StateError(RuntimeError):
    """Raised when a plan or requested state transition is invalid."""


def utc_now() -> str:
    override = os.environ.get("AGENT_WORKFLOWS_NOW")
    if override:
        return override
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise StateError(f"{label} must be a non-empty string")
    return value.strip()


def require_string_list(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty):
        qualifier = "a string list" if allow_empty else "a non-empty string list"
        raise StateError(f"{label} must be {qualifier}")
    return [require_string(item, f"{label} item") for item in value]


def load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise StateError(f"cannot read {label} at {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise StateError(f"{label} is not valid JSON: {exc}") from exc


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def read_text_at(directory_fd: int, name: str, label: str) -> str:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(name, flags, dir_fd=directory_fd)
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise StateError(f"cannot read {label} {name}: {exc}") from exc


def atomic_write_text_at(directory_fd: int, name: str, content: str) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    temporary_name = ""
    descriptor = -1
    for _attempt in range(20):
        temporary_name = f".{name}.{secrets.token_hex(8)}"
        try:
            descriptor = os.open(temporary_name, flags, 0o600, dir_fd=directory_fd)
            break
        except FileExistsError:
            continue
        except OSError as exc:
            raise StateError(f"cannot create temporary state file for {name}: {exc}") from exc
    if descriptor < 0:
        raise StateError(f"cannot allocate a temporary state file for {name}")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_name, 0o644, dir_fd=directory_fd, follow_symlinks=False)
        os.replace(
            temporary_name,
            name,
            src_dir_fd=directory_fd,
            dst_dir_fd=directory_fd,
        )
        os.fsync(directory_fd)
    finally:
        try:
            os.unlink(temporary_name, dir_fd=directory_fd)
        except FileNotFoundError:
            pass


def rename_directory_noreplace(directory_fd: int, source: str, destination: str) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    if sys.platform.startswith("linux"):
        function = getattr(libc, "renameat2", None)
        no_replace_flag = 1
    elif sys.platform == "darwin":
        function = getattr(libc, "renameatx_np", None)
        no_replace_flag = 0x00000004
    else:
        function = None
        no_replace_flag = 0
    if function is None:
        raise StateError(
            "this platform lacks atomic no-replace directory publication; "
            "initialization stopped before publishing state"
        )
    function.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_uint,
    ]
    function.restype = ctypes.c_int
    ctypes.set_errno(0)
    result = function(
        directory_fd,
        os.fsencode(source),
        directory_fd,
        os.fsencode(destination),
        no_replace_flag,
    )
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number in {errno.EEXIST, errno.ENOTEMPTY}:
        raise StateError(f"plan already exists: {destination}")
    raise StateError(
        f"cannot atomically publish plan {destination}: "
        f"{os.strerror(error_number or errno.EIO)}"
    )


def validate_slug(slug: str) -> str:
    if len(slug) > 64 or SLUG_PATTERN.fullmatch(slug) is None:
        raise StateError("slug must be lowercase kebab-case and at most 64 characters")
    return slug


def resolve_repo_root(value: str) -> Path:
    root = Path(value).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise StateError(f"repository root is not a directory: {root}")
    return root


def assert_not_symlink(path: Path, label: str) -> None:
    if path.is_symlink():
        raise StateError(f"{label} must not be a symlink: {path}")


def plan_directory(repo_root: Path, slug: str, *, require_exists: bool) -> Path:
    validate_slug(slug)
    state_root = repo_root / STATE_DIRECTORY
    goals_root = state_root / "goals"
    directory = goals_root / slug
    for path, label in (
        (state_root, "state directory"),
        (goals_root, "goals directory"),
        (directory, "plan directory"),
    ):
        if path.exists() or path.is_symlink():
            assert_not_symlink(path, label)
    if require_exists and not directory.is_dir():
        raise StateError(f"plan does not exist: {directory}")
    return directory


@contextmanager
def plan_lock(repo_root: Path, slug: str) -> Iterator[tuple[Path, int]]:
    directory = plan_directory(repo_root, slug, require_exists=True)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    opened: list[int] = []
    lock_handle = None
    try:
        current = os.open(repo_root, directory_flags | no_follow)
        opened.append(current)
        for component in (STATE_DIRECTORY, "goals", slug):
            current = os.open(
                component,
                directory_flags | no_follow,
                dir_fd=current,
            )
            opened.append(current)
        lock_descriptor = os.open(
            ".state.lock",
            os.O_RDWR | os.O_CREAT | no_follow,
            0o644,
            dir_fd=current,
        )
        lock_handle = os.fdopen(lock_descriptor, "a+", encoding="utf-8")
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        recover_pending_transaction(directory, current, slug)
        yield directory, current
    except OSError as exc:
        raise StateError(f"cannot securely open plan {directory}: {exc}") from exc
    finally:
        if lock_handle is not None:
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            lock_handle.close()
        for descriptor in reversed(opened):
            os.close(descriptor)


@contextmanager
def initialization_lock(repo_root: Path) -> Iterator[int]:
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    opened: list[int] = []
    lock_handle = None
    try:
        current = os.open(repo_root, directory_flags | no_follow)
        opened.append(current)
        for component in (STATE_DIRECTORY, "goals"):
            try:
                os.mkdir(component, 0o755, dir_fd=current)
                os.fsync(current)
            except FileExistsError:
                pass
            current = os.open(
                component,
                directory_flags | no_follow,
                dir_fd=current,
            )
            opened.append(current)
        lock_descriptor = os.open(
            ".init.lock",
            os.O_RDWR | os.O_CREAT | no_follow,
            0o644,
            dir_fd=current,
        )
        lock_handle = os.fdopen(lock_descriptor, "a+", encoding="utf-8")
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        yield current
    except OSError as exc:
        raise StateError(f"cannot securely initialize {STATE_DIRECTORY}: {exc}") from exc
    finally:
        if lock_handle is not None:
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            lock_handle.close()
        for descriptor in reversed(opened):
            os.close(descriptor)


def normalize_goal(raw: Any, label: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise StateError(f"{label} must be an object")
    expected = {"id", "title", "objective", "acceptance_criteria", "verification"}
    if set(raw) != expected:
        raise StateError(f"{label} keys must be {sorted(expected)}")
    goal_id = require_string(raw["id"], f"{label}.id")
    if GOAL_ID_PATTERN.fullmatch(goal_id) is None:
        raise StateError(f"{label}.id must match G followed by at least three digits")
    return {
        "id": goal_id,
        "title": require_string(raw["title"], f"{label}.title"),
        "objective": require_string(raw["objective"], f"{label}.objective"),
        "acceptance_criteria": require_string_list(
            raw["acceptance_criteria"], f"{label}.acceptance_criteria"
        ),
        "verification": require_string_list(raw["verification"], f"{label}.verification"),
        "status": "pending",
        "attempts": 0,
        "last_event_sequence": None,
    }


def normalize_spec(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise StateError("initialization spec must be an object")
    expected = {"objective", "constraints", "verification", "goals"}
    if set(raw) != expected:
        raise StateError(f"initialization spec keys must be {sorted(expected)}")
    goals_raw = raw["goals"]
    if not isinstance(goals_raw, list) or not goals_raw:
        raise StateError("initialization spec goals must be a non-empty list")
    goals = [normalize_goal(goal, f"goals[{index}]") for index, goal in enumerate(goals_raw)]
    ids = [goal["id"] for goal in goals]
    if len(ids) != len(set(ids)):
        raise StateError("goal IDs must be unique")
    return {
        "objective": require_string(raw["objective"], "objective"),
        "constraints": require_string_list(raw["constraints"], "constraints", allow_empty=True),
        "verification": require_string_list(raw["verification"], "verification"),
        "goals": goals,
    }


def aggregate_goal(slug: str) -> str:
    base = f"{STATE_DIRECTORY}/goals/{slug}"
    return (
        f"Complete the durable plan at {base}/goals.json under the constraints in "
        f"{base}/brief.md, checkpoint evidence in {base}/ledger.jsonl, and finish only "
        "after every accepted requirement and the final quality gate are proved."
    )


def render_brief(spec: dict[str, Any], slug: str) -> str:
    constraints = "\n".join(f"- {item}" for item in spec["constraints"]) or "- None recorded."
    verification = "\n".join(f"- {item}" for item in spec["verification"])
    return (
        f"# Goal plan: {slug}\n\n"
        f"## Objective\n\n{spec['objective']}\n\n"
        f"## Constraints\n\n{constraints}\n\n"
        f"## Global verification\n\n{verification}\n\n"
        "## Durable files\n\n"
        f"- Plan: `{STATE_DIRECTORY}/goals/{slug}/goals.json`\n"
        f"- Ledger: `{STATE_DIRECTORY}/goals/{slug}/ledger.jsonl`\n"
    )


def event_hash(event_without_hash: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(event_without_hash)).hexdigest()


def plan_hash(plan: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(plan)).hexdigest()


def build_event(
    entries: list[dict[str, Any]],
    event_type: str,
    goal_id: str | None,
    details: dict[str, Any],
    projection_hash: str,
    timestamp: str,
) -> dict[str, Any]:
    event = {
        "sequence": len(entries) + 1,
        "timestamp": timestamp,
        "event": event_type,
        "goal_id": goal_id,
        "details": json.loads(json.dumps(details, ensure_ascii=False)),
        "prev_hash": entries[-1]["hash"] if entries else None,
        "plan_hash": projection_hash,
    }
    event["hash"] = event_hash(event)
    return event


def parse_ledger(content: str) -> list[dict[str, Any]]:
    lines = content.splitlines()
    entries: list[dict[str, Any]] = []
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            raise StateError(f"ledger line {index} is empty")
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise StateError(f"ledger line {index} is invalid JSON: {exc}") from exc
        if not isinstance(event, dict):
            raise StateError(f"ledger line {index} must be an object")
        expected_keys = {
            "sequence",
            "timestamp",
            "event",
            "goal_id",
            "details",
            "prev_hash",
            "plan_hash",
            "hash",
        }
        if set(event) != expected_keys:
            raise StateError(f"ledger line {index} keys must be {sorted(expected_keys)}")
        require_string(event["timestamp"], f"ledger line {index} timestamp")
        require_string(event["event"], f"ledger line {index} event")
        if event["goal_id"] is not None:
            require_string(event["goal_id"], f"ledger line {index} goal_id")
        if not isinstance(event["details"], dict):
            raise StateError(f"ledger line {index} details must be an object")
        for field in ("plan_hash", "hash"):
            value = event[field]
            if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
                raise StateError(f"ledger line {index} {field} must be a SHA-256 digest")
        expected_hash = event.get("hash")
        payload = dict(event)
        payload.pop("hash", None)
        if event.get("sequence") != index:
            raise StateError(f"ledger line {index} has an invalid sequence")
        previous = entries[-1]["hash"] if entries else None
        if event.get("prev_hash") != previous:
            raise StateError(f"ledger line {index} breaks the hash chain")
        if expected_hash != event_hash(payload):
            raise StateError(f"ledger line {index} has an invalid hash")
        entries.append(event)
    if not entries:
        raise StateError("ledger must contain at least the plan_created event")
    return entries


def validate_plan(plan: Any) -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise StateError("goals.json must contain an object")
    expected = {
        "schema_version",
        "slug",
        "objective",
        "aggregate_goal",
        "constraints",
        "global_verification",
        "status",
        "revision",
        "created_at",
        "updated_at",
        "last_event_sequence",
        "goals",
        "final_gate",
    }
    if set(plan) != expected:
        raise StateError(f"goals.json keys must be {sorted(expected)}")
    if plan["schema_version"] != SCHEMA_VERSION:
        raise StateError(f"unsupported schema version: {plan['schema_version']}")
    validate_slug(require_string(plan["slug"], "slug"))
    require_string(plan["objective"], "objective")
    require_string(plan["aggregate_goal"], "aggregate_goal")
    if plan["aggregate_goal"] != aggregate_goal(plan["slug"]):
        raise StateError("aggregate_goal does not match the plan slug")
    require_string_list(plan["constraints"], "constraints", allow_empty=True)
    require_string_list(plan["global_verification"], "global_verification")
    if plan["status"] not in PLAN_STATUSES:
        raise StateError(f"invalid plan status: {plan['status']}")
    if not isinstance(plan["revision"], int) or plan["revision"] < 1:
        raise StateError("revision must be a positive integer")
    if not isinstance(plan["last_event_sequence"], int) or plan["last_event_sequence"] < 1:
        raise StateError("last_event_sequence must be a positive integer")
    require_string(plan["created_at"], "created_at")
    require_string(plan["updated_at"], "updated_at")
    if not isinstance(plan["goals"], list) or not plan["goals"]:
        raise StateError("goals must be a non-empty list")

    ids: set[str] = set()
    seen_open = False
    in_progress = 0
    for index, goal in enumerate(plan["goals"]):
        if not isinstance(goal, dict):
            raise StateError(f"goals[{index}] must be an object")
        goal_expected = {
            "id",
            "title",
            "objective",
            "acceptance_criteria",
            "verification",
            "status",
            "attempts",
            "last_event_sequence",
        }
        if set(goal) != goal_expected:
            raise StateError(f"goals[{index}] keys must be {sorted(goal_expected)}")
        goal_id = require_string(goal["id"], f"goals[{index}].id")
        if GOAL_ID_PATTERN.fullmatch(goal_id) is None or goal_id in ids:
            raise StateError(f"invalid or duplicate goal ID: {goal_id}")
        ids.add(goal_id)
        require_string(goal["title"], f"{goal_id}.title")
        require_string(goal["objective"], f"{goal_id}.objective")
        require_string_list(goal["acceptance_criteria"], f"{goal_id}.acceptance_criteria")
        require_string_list(goal["verification"], f"{goal_id}.verification")
        if goal["status"] not in GOAL_STATUSES:
            raise StateError(f"invalid status for {goal_id}: {goal['status']}")
        if not isinstance(goal["attempts"], int) or goal["attempts"] < 0:
            raise StateError(f"attempts for {goal_id} must be a non-negative integer")
        last_event = goal["last_event_sequence"]
        if last_event is not None and (not isinstance(last_event, int) or last_event < 1):
            raise StateError(f"last_event_sequence for {goal_id} is invalid")
        if goal["status"] == "in_progress":
            in_progress += 1
        if goal["status"] not in TERMINAL_GOAL_STATUSES:
            seen_open = True
        elif goal["status"] == "complete" and seen_open:
            raise StateError("a completed goal appears after non-terminal work")
    if in_progress > 1:
        raise StateError("only one goal may be in progress")
    if plan["status"] == "complete" and any(
        goal["status"] not in TERMINAL_GOAL_STATUSES for goal in plan["goals"]
    ):
        raise StateError("a complete plan contains non-terminal goals")
    current = next(
        (goal for goal in plan["goals"] if goal["status"] not in TERMINAL_GOAL_STATUSES),
        None,
    )
    if plan["status"] == "blocked" and (
        current is None or current["status"] != "blocked"
    ):
        raise StateError("a blocked plan must have a first blocked goal")
    if current is not None and current["status"] == "blocked" and plan["status"] != "blocked":
        raise StateError("a plan with a first blocked goal must be blocked")
    if plan["status"] == "complete":
        if plan["final_gate"] is None:
            raise StateError("a complete plan must contain a final quality gate")
        validate_quality_gate(plan["final_gate"], plan)
    elif plan["final_gate"] is not None:
        raise StateError("an incomplete plan must not contain a final quality gate")
    return plan


def validate_projection(plan: dict[str, Any], entries: list[dict[str, Any]]) -> None:
    if plan["last_event_sequence"] != entries[-1]["sequence"]:
        raise StateError("goals.json and ledger.jsonl disagree on the last event")
    if plan["revision"] != len(entries):
        raise StateError("goals.json revision and ledger length disagree")
    if entries[-1].get("plan_hash") != plan_hash(plan):
        raise StateError("goals.json does not match the ledger projection hash")


def parse_plan(content: str, label: str) -> dict[str, Any]:
    try:
        return validate_plan(json.loads(content))
    except json.JSONDecodeError as exc:
        raise StateError(f"{label} is not valid JSON: {exc}") from exc


def load_state(
    directory: Path,
    directory_fd: int,
    expected_slug: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    plan_text = read_text_at(directory_fd, "goals.json", "goals file")
    plan = parse_plan(plan_text, "goals file")
    if plan["slug"] != expected_slug:
        raise StateError(
            f"goals.json slug {plan['slug']} does not match directory {expected_slug}"
        )
    entries = parse_ledger(read_text_at(directory_fd, "ledger.jsonl", "ledger file"))
    validate_projection(plan, entries)
    expected_brief = render_brief(
        {
            "objective": plan["objective"],
            "constraints": plan["constraints"],
            "verification": plan["global_verification"],
        },
        plan["slug"],
    )
    if read_text_at(directory_fd, "brief.md", "brief file") != expected_brief:
        raise StateError("brief.md does not match the durable plan")
    return plan, entries


def recover_pending_transaction(directory: Path, directory_fd: int, expected_slug: str) -> None:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(TRANSACTION_FILE, flags, dir_fd=directory_fd)
    except FileNotFoundError:
        return
    except OSError as exc:
        raise StateError(f"cannot inspect pending transaction in {directory}: {exc}") from exc
    with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
        content = handle.read()
    try:
        transaction = json.loads(content)
    except json.JSONDecodeError as exc:
        raise StateError(f"pending transaction is not valid JSON: {exc}") from exc
    if not isinstance(transaction, dict) or set(transaction) != {
        "schema_version",
        "plan",
        "ledger",
    }:
        raise StateError("pending transaction has an invalid shape")
    if transaction["schema_version"] != SCHEMA_VERSION:
        raise StateError("pending transaction has an unsupported schema version")
    plan = validate_plan(transaction["plan"])
    if plan["slug"] != expected_slug:
        raise StateError(
            f"pending transaction slug {plan['slug']} does not match directory {expected_slug}"
        )
    ledger = transaction["ledger"]
    if not isinstance(ledger, list):
        raise StateError("pending transaction ledger must be a list")
    ledger_text = "".join(
        json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in ledger
    )
    entries = parse_ledger(ledger_text)
    validate_projection(plan, entries)
    if len(entries) < 2:
        raise StateError("pending transaction must contain exactly one state mutation")
    previous_entries = entries[:-1]
    if entries[-1]["prev_hash"] != previous_entries[-1]["hash"]:
        raise StateError("pending transaction does not extend its predecessor ledger")

    current_plan = parse_plan(
        read_text_at(directory_fd, "goals.json", "current goals file"),
        "current goals file",
    )
    if current_plan["slug"] != expected_slug:
        raise StateError("current goals file slug does not match its directory")
    current_entries = parse_ledger(
        read_text_at(directory_fd, "ledger.jsonl", "current ledger file")
    )
    previous_plan_hash = previous_entries[-1]["plan_hash"]
    final_plan_hash = entries[-1]["plan_hash"]
    current_plan_hash = plan_hash(current_plan)
    if current_plan_hash == previous_plan_hash:
        if current_plan["revision"] != len(previous_entries):
            raise StateError("current predecessor plan revision is invalid")
    elif current_plan_hash == final_plan_hash:
        if current_plan["revision"] != len(entries):
            raise StateError("current final plan revision is invalid")
    else:
        raise StateError("pending transaction does not extend the current plan")
    if current_entries != previous_entries and current_entries != entries:
        raise StateError("pending transaction does not extend the current ledger")

    if current_plan_hash != final_plan_hash or current_entries != entries:
        atomic_write_text_at(directory_fd, "ledger.jsonl", ledger_text)
        atomic_write_text_at(directory_fd, "goals.json", json_text(plan))
    os.unlink(TRANSACTION_FILE, dir_fd=directory_fd)
    os.fsync(directory_fd)


def write_mutation(
    directory: Path,
    directory_fd: int,
    plan: dict[str, Any],
    entries: list[dict[str, Any]],
    event_type: str,
    goal_id: str | None,
    details: dict[str, Any],
) -> dict[str, Any]:
    timestamp = utc_now()
    plan["revision"] += 1
    plan["updated_at"] = timestamp
    plan["last_event_sequence"] = len(entries) + 1
    if goal_id is not None:
        goal_by_id(plan, goal_id)["last_event_sequence"] = len(entries) + 1
    validate_plan(plan)
    event = build_event(
        entries,
        event_type,
        goal_id,
        details,
        plan_hash(plan),
        timestamp,
    )
    entries = [*entries, event]
    ledger_text = "".join(
        json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n" for item in entries
    )
    transaction = {
        "schema_version": SCHEMA_VERSION,
        "plan": plan,
        "ledger": entries,
    }
    atomic_write_text_at(directory_fd, TRANSACTION_FILE, json_text(transaction))
    atomic_write_text_at(directory_fd, "ledger.jsonl", ledger_text)
    atomic_write_text_at(directory_fd, "goals.json", json_text(plan))
    os.unlink(TRANSACTION_FILE, dir_fd=directory_fd)
    os.fsync(directory_fd)
    return event


def check_revision(plan: dict[str, Any], expected: int) -> None:
    if plan["revision"] != expected:
        raise StateError(
            f"revision mismatch: expected {expected}, current {plan['revision']}; run status and retry"
        )


def goal_by_id(plan: dict[str, Any], goal_id: str) -> dict[str, Any]:
    for goal in plan["goals"]:
        if goal["id"] == goal_id:
            return goal
    raise StateError(f"unknown goal ID: {goal_id}")


def first_non_terminal(plan: dict[str, Any]) -> dict[str, Any] | None:
    return next(
        (goal for goal in plan["goals"] if goal["status"] not in TERMINAL_GOAL_STATUSES),
        None,
    )


def status_payload(directory: Path, plan: dict[str, Any]) -> dict[str, Any]:
    current = first_non_terminal(plan)
    counts = {status: 0 for status in sorted(GOAL_STATUSES)}
    for goal in plan["goals"]:
        counts[goal["status"]] += 1
    return {
        "path": str(directory),
        "slug": plan["slug"],
        "status": plan["status"],
        "revision": plan["revision"],
        "aggregate_goal": plan["aggregate_goal"],
        "goal_counts": counts,
        "current_goal": current,
        "ready_to_finalize": current is None and plan["status"] != "complete",
    }


def validate_complete_evidence(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise StateError("completion evidence must be an object")
    expected = {"summary", "artifacts", "checks", "residual_risks"}
    if set(raw) != expected:
        raise StateError(f"completion evidence keys must be {sorted(expected)}")
    checks = raw["checks"]
    if not isinstance(checks, list) or not checks:
        raise StateError("completion evidence checks must be a non-empty list")
    normalized_checks = []
    for index, check in enumerate(checks):
        if not isinstance(check, dict) or set(check) != {"name", "status", "evidence"}:
            raise StateError(f"checks[{index}] must contain name, status, and evidence")
        status = require_string(check["status"], f"checks[{index}].status")
        if status not in {"passed", "failed"}:
            raise StateError(f"checks[{index}].status must be passed or failed")
        normalized_checks.append(
            {
                "name": require_string(check["name"], f"checks[{index}].name"),
                "status": status,
                "evidence": require_string(check["evidence"], f"checks[{index}].evidence"),
            }
        )
    if any(check["status"] != "passed" for check in normalized_checks):
        raise StateError("completion evidence contains a failed check")
    return {
        "summary": require_string(raw["summary"], "summary"),
        "artifacts": require_string_list(raw["artifacts"], "artifacts"),
        "checks": normalized_checks,
        "residual_risks": require_string_list(
            raw["residual_risks"], "residual_risks", allow_empty=True
        ),
    }


def validate_blocker_evidence(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise StateError("blocker evidence must be an object")
    expected = {"summary", "blocker", "attempts", "needed_action"}
    if set(raw) != expected:
        raise StateError(f"blocker evidence keys must be {sorted(expected)}")
    return {
        "summary": require_string(raw["summary"], "summary"),
        "blocker": require_string(raw["blocker"], "blocker"),
        "attempts": require_string_list(raw["attempts"], "attempts"),
        "needed_action": require_string(raw["needed_action"], "needed_action"),
    }


def validate_quality_gate(raw: Any, plan: dict[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise StateError("quality gate must be an object")
    expected = {
        "status",
        "implementation_changed",
        "requirements",
        "verification",
        "review",
        "residual_risks",
    }
    if set(raw) != expected:
        raise StateError(f"quality gate keys must be {sorted(expected)}")
    if raw["status"] != "passed":
        raise StateError("quality gate status must be passed")
    requirements = raw["requirements"]
    if not isinstance(requirements, list) or not requirements:
        raise StateError("quality gate requirements must be a non-empty list")
    normalized_requirements = []
    for index, item in enumerate(requirements):
        if not isinstance(item, dict) or set(item) != {"requirement", "status", "evidence"}:
            raise StateError(
                f"requirements[{index}] must contain requirement, status, and evidence"
            )
        requirement = require_string(
            item["requirement"], f"requirements[{index}].requirement"
        )
        if item["status"] != "proved":
            raise StateError(f"requirements[{index}].status must be proved")
        normalized_requirements.append(
            {
                "requirement": requirement,
                "status": "proved",
                "evidence": require_string(
                    item["evidence"], f"requirements[{index}].evidence"
                ),
            }
        )
    verification = raw["verification"]
    if not isinstance(verification, list) or not verification:
        raise StateError("quality gate verification must be a non-empty list")
    normalized_verification = []
    for index, item in enumerate(verification):
        if not isinstance(item, dict) or set(item) != {"name", "status", "evidence"}:
            raise StateError(f"verification[{index}] must contain name, status, and evidence")
        name = require_string(item["name"], f"verification[{index}].name")
        if item["status"] != "passed":
            raise StateError(f"verification[{index}].status must be passed")
        normalized_verification.append(
            {
                "name": name,
                "status": "passed",
                "evidence": require_string(
                    item["evidence"], f"verification[{index}].evidence"
                ),
            }
        )
    implementation_changed = raw["implementation_changed"]
    if not isinstance(implementation_changed, bool):
        raise StateError("quality gate implementation_changed must be a boolean")
    review = raw["review"]
    if not isinstance(review, dict) or set(review) != {"status", "evidence"}:
        raise StateError("quality gate review must contain status and evidence")
    expected_review_status = "passed" if implementation_changed else "not_required"
    if review["status"] != expected_review_status:
        raise StateError(
            f"quality gate review status must be {expected_review_status} when "
            f"implementation_changed is {str(implementation_changed).lower()}"
        )
    normalized_review = {
        "status": expected_review_status,
        "evidence": require_string(review["evidence"], "review.evidence"),
    }
    residual_risks = require_string_list(
        raw["residual_risks"], "residual_risks", allow_empty=True
    )
    if plan is not None:
        required_requirements = [plan["objective"], *plan["constraints"]]
        required_verification = list(plan["global_verification"])
        for goal in plan["goals"]:
            if goal["status"] != "complete":
                continue
            required_requirements.extend(goal["acceptance_criteria"])
            required_verification.extend(goal["verification"])
        provided_requirements = [item["requirement"] for item in normalized_requirements]
        provided_verification = [item["name"] for item in normalized_verification]
        if len(provided_requirements) != len(set(provided_requirements)):
            raise StateError("quality gate requirements must not contain duplicates")
        if len(provided_verification) != len(set(provided_verification)):
            raise StateError("quality gate verification must not contain duplicates")
        missing_requirements = sorted(set(required_requirements) - set(provided_requirements))
        if missing_requirements:
            raise StateError(
                f"quality gate does not prove required requirements: {missing_requirements}"
            )
        missing_verification = sorted(
            set(required_verification) - set(provided_verification)
        )
        if missing_verification:
            raise StateError(
                f"quality gate does not cover required verification: {missing_verification}"
            )
    return {
        "status": "passed",
        "implementation_changed": implementation_changed,
        "requirements": normalized_requirements,
        "verification": normalized_verification,
        "review": normalized_review,
        "residual_risks": residual_risks,
    }


def completed_goal_snapshot(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise StateError("goal snapshot must be an object")
    candidates = []
    if "objective" in raw or "status" in raw:
        candidates.append(raw)
    nested = raw.get("goal")
    if nested is not None:
        if not isinstance(nested, dict):
            raise StateError("goal snapshot goal must be an object")
        candidates.append(nested)
    valid = [
        candidate
        for candidate in candidates
        if isinstance(candidate.get("objective"), str)
        and isinstance(candidate.get("status"), str)
    ]
    if len(valid) != 1:
        raise StateError("goal snapshot must contain exactly one explicit goal object")
    return {
        "objective": require_string(valid[0]["objective"], "goal snapshot objective"),
        "status": require_string(valid[0]["status"], "goal snapshot status"),
    }


def command_init(repo_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    validate_slug(args.slug)
    directory = repo_root / STATE_DIRECTORY / "goals" / args.slug
    spec = normalize_spec(load_json(Path(args.spec), "initialization spec"))
    timestamp = utc_now()
    plan = {
        "schema_version": SCHEMA_VERSION,
        "slug": args.slug,
        "objective": spec["objective"],
        "aggregate_goal": aggregate_goal(args.slug),
        "constraints": spec["constraints"],
        "global_verification": spec["verification"],
        "status": "active",
        "revision": 1,
        "created_at": timestamp,
        "updated_at": timestamp,
        "last_event_sequence": 1,
        "goals": spec["goals"],
        "final_gate": None,
    }
    validate_plan(plan)
    initial_event = build_event(
        [],
        "plan_created",
        None,
        {"goal_count": len(spec["goals"]), "slug": args.slug},
        plan_hash(plan),
        timestamp,
    )
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    no_follow = getattr(os, "O_NOFOLLOW", 0)
    with initialization_lock(repo_root) as goals_fd:
        try:
            existing_fd = os.open(
                args.slug,
                directory_flags | no_follow,
                dir_fd=goals_fd,
            )
        except FileNotFoundError:
            existing_fd = None
        except OSError as exc:
            raise StateError(f"cannot inspect plan destination {directory}: {exc}") from exc
        if existing_fd is not None:
            os.close(existing_fd)
            raise StateError(f"plan already exists: {directory}")

        temporary_name = f".{args.slug}.{secrets.token_hex(8)}"
        os.mkdir(temporary_name, 0o755, dir_fd=goals_fd)
        temporary_fd = os.open(
            temporary_name,
            directory_flags | no_follow,
            dir_fd=goals_fd,
        )
        published = False
        try:
            atomic_write_text_at(temporary_fd, "brief.md", render_brief(spec, args.slug))
            atomic_write_text_at(temporary_fd, "goals.json", json_text(plan))
            atomic_write_text_at(
                temporary_fd,
                "ledger.jsonl",
                json.dumps(initial_event, ensure_ascii=False, sort_keys=True) + "\n",
            )
            lock_fd = os.open(
                ".state.lock",
                os.O_RDWR | os.O_CREAT | os.O_EXCL | no_follow,
                0o644,
                dir_fd=temporary_fd,
            )
            os.close(lock_fd)
            os.fsync(temporary_fd)
            rename_directory_noreplace(goals_fd, temporary_name, args.slug)
            os.fsync(goals_fd)
            published = True
        finally:
            os.close(temporary_fd)
            if not published:
                for name in ("brief.md", "goals.json", "ledger.jsonl", ".state.lock"):
                    try:
                        os.unlink(f"{temporary_name}/{name}", dir_fd=goals_fd)
                    except FileNotFoundError:
                        pass
                try:
                    os.rmdir(temporary_name, dir_fd=goals_fd)
                except FileNotFoundError:
                    pass
    return status_payload(directory, plan)


def command_status(repo_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    with plan_lock(repo_root, args.slug) as (directory, directory_fd):
        plan, _entries = load_state(directory, directory_fd, args.slug)
    return status_payload(directory, plan)


def command_validate(repo_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    with plan_lock(repo_root, args.slug) as (directory, directory_fd):
        plan, entries = load_state(directory, directory_fd, args.slug)
    return {
        "valid": True,
        "path": str(directory),
        "revision": plan["revision"],
        "ledger_events": len(entries),
    }


def command_start(repo_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    with plan_lock(repo_root, args.slug) as (directory, directory_fd):
        plan, entries = load_state(directory, directory_fd, args.slug)
        check_revision(plan, args.expected_revision)
        current = first_non_terminal(plan)
        if current is None:
            raise StateError("all goals are terminal; run the final quality gate")
        if args.goal_id and current["id"] != args.goal_id:
            raise StateError(f"the next eligible goal is {current['id']}, not {args.goal_id}")
        if current["status"] == "blocked":
            raise StateError(f"{current['id']} is blocked; resume or replace it first")
        if current["status"] == "in_progress":
            raise StateError(f"{current['id']} is already in progress")
        current["status"] = "in_progress"
        current["attempts"] += 1
        plan["status"] = "active"
        write_mutation(
            directory,
            directory_fd,
            plan,
            entries,
            "goal_started",
            current["id"],
            {"attempt": current["attempts"]},
        )
    return status_payload(directory, plan)


def command_checkpoint(repo_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    with plan_lock(repo_root, args.slug) as (directory, directory_fd):
        plan, entries = load_state(directory, directory_fd, args.slug)
        check_revision(plan, args.expected_revision)
        goal = goal_by_id(plan, args.goal_id)
        if goal["status"] != "in_progress":
            raise StateError(f"{args.goal_id} must be in_progress before checkpointing")
        raw_evidence = load_json(Path(args.evidence_file), "checkpoint evidence")
        if args.status == "complete":
            evidence = validate_complete_evidence(raw_evidence)
            event_type = "goal_completed"
        else:
            evidence = validate_blocker_evidence(raw_evidence)
            event_type = "goal_blocked"
        goal["status"] = args.status
        plan["status"] = "blocked" if args.status == "blocked" else "active"
        write_mutation(
            directory,
            directory_fd,
            plan,
            entries,
            event_type,
            goal["id"],
            evidence,
        )
    return status_payload(directory, plan)


def command_resume(repo_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    reason = require_string(args.reason, "reason")
    with plan_lock(repo_root, args.slug) as (directory, directory_fd):
        plan, entries = load_state(directory, directory_fd, args.slug)
        check_revision(plan, args.expected_revision)
        goal = goal_by_id(plan, args.goal_id)
        if goal["status"] != "blocked":
            raise StateError(f"{args.goal_id} must be blocked before resuming")
        if first_non_terminal(plan)["id"] != goal["id"]:
            raise StateError(f"{args.goal_id} is not the first non-terminal goal")
        goal["status"] = "in_progress"
        goal["attempts"] += 1
        plan["status"] = "active"
        write_mutation(
            directory,
            directory_fd,
            plan,
            entries,
            "goal_resumed",
            goal["id"],
            {"attempt": goal["attempts"], "reason": reason},
        )
    return status_payload(directory, plan)


def load_new_goal(path: str, plan: dict[str, Any], label: str) -> dict[str, Any]:
    goal = normalize_goal(load_json(Path(path), label), label)
    if any(existing["id"] == goal["id"] for existing in plan["goals"]):
        raise StateError(f"goal ID already exists: {goal['id']}")
    return goal


def command_append(repo_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    reason = require_string(args.reason, "reason")
    with plan_lock(repo_root, args.slug) as (directory, directory_fd):
        plan, entries = load_state(directory, directory_fd, args.slug)
        check_revision(plan, args.expected_revision)
        if plan["status"] == "complete":
            raise StateError("cannot append to a complete plan")
        goal = load_new_goal(args.goal_file, plan, "appended goal")
        plan["goals"].append(goal)
        write_mutation(
            directory,
            directory_fd,
            plan,
            entries,
            "goal_appended",
            goal["id"],
            {"reason": reason, "goal": goal},
        )
    return status_payload(directory, plan)


def command_replace(repo_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    reason = require_string(args.reason, "reason")
    with plan_lock(repo_root, args.slug) as (directory, directory_fd):
        plan, entries = load_state(directory, directory_fd, args.slug)
        check_revision(plan, args.expected_revision)
        original = goal_by_id(plan, args.goal_id)
        if original["status"] not in {"pending", "blocked"}:
            raise StateError("only pending or blocked goals may be replaced")
        replacement = load_new_goal(args.goal_file, plan, "replacement goal")
        index = plan["goals"].index(original)
        original["status"] = "superseded"
        replacement["last_event_sequence"] = len(entries) + 1
        plan["goals"].insert(index + 1, replacement)
        current = first_non_terminal(plan)
        plan["status"] = (
            "blocked" if current is not None and current["status"] == "blocked" else "active"
        )
        write_mutation(
            directory,
            directory_fd,
            plan,
            entries,
            "goal_replaced",
            original["id"],
            {
                "reason": reason,
                "replacement_goal_id": replacement["id"],
                "replacement": replacement,
            },
        )
    return status_payload(directory, plan)


def command_finalize(repo_root: Path, args: argparse.Namespace) -> dict[str, Any]:
    with plan_lock(repo_root, args.slug) as (directory, directory_fd):
        plan, entries = load_state(directory, directory_fd, args.slug)
        check_revision(plan, args.expected_revision)
        if plan["status"] == "complete":
            raise StateError("plan is already complete")
        remaining = [
            goal["id"] for goal in plan["goals"] if goal["status"] not in TERMINAL_GOAL_STATUSES
        ]
        if remaining:
            raise StateError(f"cannot finalize with non-terminal goals: {remaining}")
        gate = validate_quality_gate(
            load_json(Path(args.quality_gate_file), "quality gate"),
            plan,
        )
        snapshot = completed_goal_snapshot(
            load_json(Path(args.goal_snapshot_file), "completed goal snapshot")
        )
        if snapshot["status"] != "complete":
            raise StateError("native goal snapshot status must be complete")
        if snapshot["objective"] not in {plan["objective"], plan["aggregate_goal"]}:
            raise StateError("native goal snapshot objective does not match this plan")
        plan["status"] = "complete"
        plan["final_gate"] = gate
        write_mutation(
            directory,
            directory_fd,
            plan,
            entries,
            "plan_completed",
            None,
            {"quality_gate": gate, "native_goal": snapshot},
        )
    return status_payload(directory, plan)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=".", help="Target repository root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="Create a new durable goal plan")
    init.add_argument("--slug", required=True)
    init.add_argument("--spec", required=True)
    init.set_defaults(handler=command_init)

    for name, handler in (("status", command_status), ("validate", command_validate)):
        command = subparsers.add_parser(name)
        command.add_argument("--slug", required=True)
        command.set_defaults(handler=handler)

    start = subparsers.add_parser("start", help="Start the first non-terminal goal")
    start.add_argument("--slug", required=True)
    start.add_argument("--expected-revision", required=True, type=int)
    start.add_argument("--goal-id")
    start.set_defaults(handler=command_start)

    checkpoint = subparsers.add_parser("checkpoint", help="Complete or block an active goal")
    checkpoint.add_argument("--slug", required=True)
    checkpoint.add_argument("--expected-revision", required=True, type=int)
    checkpoint.add_argument("--goal-id", required=True)
    checkpoint.add_argument("--status", choices=("complete", "blocked"), required=True)
    checkpoint.add_argument("--evidence-file", required=True)
    checkpoint.set_defaults(handler=command_checkpoint)

    resume = subparsers.add_parser("resume", help="Resume the first blocked goal")
    resume.add_argument("--slug", required=True)
    resume.add_argument("--expected-revision", required=True, type=int)
    resume.add_argument("--goal-id", required=True)
    resume.add_argument("--reason", required=True)
    resume.set_defaults(handler=command_resume)

    append = subparsers.add_parser("append", help="Append evidence-backed pending work")
    append.add_argument("--slug", required=True)
    append.add_argument("--expected-revision", required=True, type=int)
    append.add_argument("--goal-file", required=True)
    append.add_argument("--reason", required=True)
    append.set_defaults(handler=command_append)

    replace = subparsers.add_parser("replace", help="Replace pending or blocked work")
    replace.add_argument("--slug", required=True)
    replace.add_argument("--expected-revision", required=True, type=int)
    replace.add_argument("--goal-id", required=True)
    replace.add_argument("--goal-file", required=True)
    replace.add_argument("--reason", required=True)
    replace.set_defaults(handler=command_replace)

    finalize = subparsers.add_parser("finalize", help="Reconcile a complete native goal")
    finalize.add_argument("--slug", required=True)
    finalize.add_argument("--expected-revision", required=True, type=int)
    finalize.add_argument("--quality-gate-file", required=True)
    finalize.add_argument("--goal-snapshot-file", required=True)
    finalize.set_defaults(handler=command_finalize)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        repo_root = resolve_repo_root(args.repo_root)
        payload = args.handler(repo_root, args)
    except StateError as exc:
        parser.exit(2, f"ERROR: {exc}\n")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
