#!/usr/bin/env python3
"""Collect bounded Git and documentation evidence for project history work."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ANCHOR_RE = re.compile(
    r"<!--\s*project-chronicle:last-recorded-commit:\s*([^\s]+)\s*-->"
)
HISTORY_CANDIDATES = (Path("docs/project-history"), Path("docs/history"))
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".next",
    ".nuxt",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
DOC_SUFFIXES = {".md", ".mdx", ".rst", ".adoc", ".txt"}
ROOT_DOC_PREFIXES = (
    "README",
    "AGENTS",
    "CHANGELOG",
    "HISTORY",
    "CONTEXT",
    "ARCHITECTURE",
    "DECISIONS",
    "HANDOFF",
)
COMMIT_RECORD_TOKEN = "PROJECT_CHRONICLE_COMMIT"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect Git and repository-document evidence without modifying the project."
    )
    parser.add_argument("--project-root", required=True, help="Repository or project root")
    parser.add_argument(
        "--history-path",
        help="Explicit history directory, absolute or relative to project root",
    )
    parser.add_argument(
        "--since",
        default="auto",
        help="Lower Git revision (exclusive), or 'auto' to read the LOG.md anchor",
    )
    parser.add_argument(
        "--until", default="HEAD", help="Upper Git revision (inclusive, default: HEAD)"
    )
    parser.add_argument(
        "--max-commits",
        type=int,
        default=500,
        help="Maximum commits returned before reporting truncation (default: 500)",
    )
    parser.add_argument(
        "--max-documents",
        type=int,
        default=400,
        help="Maximum documentation paths returned (default: 400)",
    )
    parser.add_argument(
        "--format", choices=("json", "summary"), default="json", help="Output format"
    )
    return parser.parse_args()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_history_path(root: Path, explicit: str | None) -> tuple[Path, str]:
    if explicit:
        candidate = Path(explicit)
        if not candidate.is_absolute():
            candidate = root / candidate
        candidate = candidate.resolve()
        if not is_within(candidate, root):
            raise ValueError("history path must stay inside project root")
        return candidate, "explicit"

    for relative in HISTORY_CANDIDATES:
        candidate = (root / relative).resolve()
        if is_within(candidate, root) and is_chronicle_directory(candidate):
            return candidate, "existing"
    default = (root / HISTORY_CANDIDATES[0]).resolve()
    if not is_within(default, root):
        raise ValueError("default history path resolves outside project root")
    return default, "default"


def has_heading(text: str, heading: str) -> bool:
    return re.search(rf"^{re.escape(heading)}\s*$", text, re.MULTILINE) is not None


def is_chronicle_directory(candidate: Path) -> bool:
    if not candidate.is_dir():
        return False
    log_path = candidate / "LOG.md"
    if log_path.is_file() and ANCHOR_RE.search(
        log_path.read_text(encoding="utf-8", errors="replace")
    ):
        return True
    readme_path = candidate / "README.md"
    timeline_path = candidate / "TIMELINE.md"
    if not readme_path.is_file() or not timeline_path.is_file():
        return False
    readme = readme_path.read_text(encoding="utf-8", errors="replace")
    timeline = timeline_path.read_text(encoding="utf-8", errors="replace")
    return has_heading(readme, "# Project History") and has_heading(
        timeline, "# Project Timeline"
    )


def run_git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def git_value(root: Path, *args: str) -> str | None:
    result = run_git(root, *args)
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def read_anchor(history_path: Path) -> str | None:
    log_path = history_path / "LOG.md"
    if not log_path.is_file():
        return None
    match = ANCHOR_RE.search(log_path.read_text(encoding="utf-8", errors="replace"))
    if not match:
        return None
    value = match.group(1)
    return None if value == "none" else value


def verify_revision(root: Path, revision: str) -> str:
    result = run_git(root, "rev-parse", "--verify", f"{revision}^{{commit}}")
    if result.returncode != 0:
        detail = result.stderr.strip() or "revision did not resolve"
        raise ValueError(f"invalid Git revision {revision!r}: {detail}")
    return result.stdout.strip()


def is_ancestor(root: Path, older: str | None, newer: str | None) -> bool | None:
    if not older or not newer:
        return None
    result = run_git(root, "merge-base", "--is-ancestor", older, newer)
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def collect_commits(
    root: Path, since: str | None, until: str, max_commits: int
) -> tuple[list[dict[str, Any]], bool, str]:
    revision_range = f"{since}..{until}" if since else until
    command = [
        "log",
        "-z",
        "--date=iso-strict",
        "--no-renames",
        "--relative",
        f"--max-count={max_commits + 1}",
        f"--format=%x00{COMMIT_RECORD_TOKEN}%x00%H%x00%aI%x00%an%x00%P%x00%s%x00",
        "--name-only",
        revision_range,
        "--",
        ".",
    ]
    result = run_git(root, *command)
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or "git log failed")

    commits: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    first_path_after_header = False
    tokens = result.stdout.split("\x00")
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == COMMIT_RECORD_TOKEN and index > 0 and tokens[index - 1] == "":
            if current is not None:
                current["paths"] = sorted(set(current["paths"]))
                commits.append(current)
            fields = tokens[index + 1 : index + 6]
            if len(fields) != 5:
                raise ValueError("unexpected git log record format")
            commit_hash, authored_at, author, parents, subject = fields
            current = {
                "hash": commit_hash,
                "authored_at": authored_at,
                "author": author,
                "parents": parents.split() if parents else [],
                "subject": subject,
                "paths": [],
            }
            first_path_after_header = True
            index += 6
            continue
        if current is not None:
            path = token
            if path and first_path_after_header:
                path = path[1:] if path.startswith("\n") else path
                first_path_after_header = False
            if path:
                current["paths"].append(path)
        index += 1
    if current is not None:
        current["paths"] = sorted(set(current["paths"]))
        commits.append(current)

    truncated = len(commits) > max_commits
    return commits[:max_commits], truncated, revision_range


def collect_tags(root: Path, *, scoped: bool) -> list[dict[str, str]]:
    result = run_git(
        root,
        "for-each-ref",
        "--sort=-creatordate",
        "--format=%(refname:short)%09%(creatordate:iso-strict)%09%(objectname)",
        "refs/tags",
    )
    if result.returncode != 0:
        return []
    tags: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) == 3 and (
            not scoped or revision_directly_touches_scope(root, fields[0])
        ):
            tags.append({"name": fields[0], "created_at": fields[1], "object": fields[2]})
    return tags


def revision_directly_touches_scope(root: Path, revision: str) -> bool:
    result = run_git(
        root,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-only",
        "--no-renames",
        "-r",
        "-m",
        f"{revision}^{{commit}}",
        "--",
        ".",
    )
    return result.returncode == 0 and bool(result.stdout.strip())


def is_document_candidate(relative: Path) -> bool:
    if relative.suffix.lower() not in DOC_SUFFIXES:
        return False
    if len(relative.parts) == 1:
        return relative.name.upper().startswith(ROOT_DOC_PREFIXES)
    if relative.parts[0] in {"docs", "documentation", "doc", "_memory"}:
        return True
    lowered = {part.lower() for part in relative.parts[:-1]}
    return bool(lowered & {"adr", "adrs", "decisions", "history", "handoffs"})


def collect_documents(root: Path, limit: int) -> tuple[list[str], bool]:
    documents: list[str] = []
    for current_root, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in SKIP_DIRS)
        current = Path(current_root)
        for filename in sorted(filenames):
            path = current / filename
            try:
                relative = path.relative_to(root)
            except ValueError:
                continue
            if is_document_candidate(relative):
                documents.append(relative.as_posix())
    documents.sort()
    return documents[:limit], len(documents) > limit


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"project root is not a directory: {root}")
    if args.max_commits < 1 or args.max_documents < 1:
        raise ValueError("maximum counts must be positive")

    history_path, history_source = resolve_history_path(root, args.history_path)
    documents, documents_truncated = collect_documents(root, args.max_documents)
    payload: dict[str, Any] = {
        "schema_version": 2,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": str(root),
        "history": {
            "path": history_path.relative_to(root).as_posix(),
            "selection": history_source,
            "exists": history_path.is_dir(),
        },
        "documents": {"paths": documents, "truncated": documents_truncated},
    }

    inside = run_git(root, "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        payload["git"] = {
            "available": False,
            "reason": inside.stderr.strip() or "not inside a Git work tree",
        }
        return payload

    anchor = read_anchor(history_path) if args.since == "auto" else args.since
    resolved_anchor = verify_revision(root, anchor) if anchor else None
    actual_head = git_value(root, "rev-parse", "--verify", "HEAD")
    if actual_head is None and args.until == "HEAD":
        resolved_until = None
        commits: list[dict[str, Any]] = []
        commits_truncated = False
        revision_range = "unborn HEAD"
    else:
        resolved_until = verify_revision(root, args.until)
        commits, commits_truncated, revision_range = collect_commits(
            root, resolved_anchor, resolved_until, args.max_commits
        )
    status_result = run_git(
        root, "status", "--short", "--branch", "--untracked-files=all", "--", "."
    )
    git_root = git_value(root, "rev-parse", "--show-toplevel")
    scope_path = "."
    if git_root:
        scope_path = root.relative_to(Path(git_root).resolve()).as_posix() or "."
    roots = (
        git_value(
            root,
            "rev-list",
            "--max-parents=0",
            "--reverse",
            resolved_until,
            "--",
            ".",
        )
        if resolved_until
        else None
    )

    payload["git"] = {
        "available": True,
        "root": git_root,
        "scope": {
            "kind": "repository" if scope_path == "." else "subdirectory",
            "path": scope_path,
        },
        "branch": git_value(root, "branch", "--show-current"),
        "head": actual_head,
        "range_until": resolved_until,
        "base_anchor": resolved_anchor,
        "anchor_is_ancestor": is_ancestor(root, resolved_anchor, resolved_until),
        "revision_range": revision_range,
        "status": status_result.stdout.splitlines(),
        "dirty": bool(status_result.stdout.splitlines()[1:])
        if status_result.stdout.startswith("## ")
        else bool(status_result.stdout.strip()),
        "root_commits": roots.splitlines() if roots else [],
        "commits": commits,
        "commits_truncated": commits_truncated,
        "tags": collect_tags(root, scoped=scope_path != "."),
    }
    return payload


def print_summary(payload: dict[str, Any]) -> None:
    print(f"project_root: {payload['project_root']}")
    history = payload["history"]
    print(
        f"history: {history['path']} (selection={history['selection']}, exists={history['exists']})"
    )
    documents = payload["documents"]
    print(
        f"documents: {len(documents['paths'])}"
        + (" (truncated)" if documents["truncated"] else "")
    )
    git = payload["git"]
    if not git["available"]:
        print(f"git: unavailable ({git['reason']})")
        return
    print(f"git_head: {git['head']}")
    if git["range_until"] != git["head"]:
        print(f"range_until: {git['range_until']}")
    print(f"git_scope: {git['scope']['kind']} ({git['scope']['path']})")
    print(f"base_anchor: {git['base_anchor'] or 'none'}")
    print(f"anchor_is_ancestor: {git['anchor_is_ancestor']}")
    print(f"range: {git['revision_range']}")
    print(
        f"commits: {len(git['commits'])}"
        + (" (truncated)" if git["commits_truncated"] else "")
    )
    print(f"dirty: {git['dirty']}")
    print(f"tags: {len(git['tags'])}")


def main() -> int:
    args = parse_args()
    try:
        payload = build_payload(args)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
