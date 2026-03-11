#!/usr/bin/env python3
"""Resolve a canonical repo-local HANDOFF path for a project."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_RELATIVE_PATH = Path("docs") / "HANDOFF.md"
RECOGNIZED_RELATIVE_PATHS = (
    Path("docs") / "HANDOFF.md",
    Path("memories") / "HANDOFF.md",
    Path("HANDOFF.md"),
)
INITIAL_CONTENT = """# HANDOFF

## Metadata

- Project:
- Project ID:
- Repo Root:
- Branch:
- Last Updated:
- Updated By:

## Current Objective

## Current State

## Important Context

- Key decisions:
- Constraints:
- Relevant files:
- Useful commands:

## Changes Made

## Validation

- Tests run:
- Results:
- Not run yet:

## Open Questions / Risks

## Next Actions

1.

## Resume Prompt

Continue this project from the shared HANDOFF document. First verify the repo still matches the notes, then execute the next action.
"""


def run_git(project_root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def canonical_project_root(project_root: Path) -> Path:
    top_level = run_git(project_root, "rev-parse", "--show-toplevel")
    if top_level:
        return Path(top_level).resolve()
    return project_root


def resolve_explicit_handoff_path(project_root: Path, handoff_path: str) -> Path:
    candidate = Path(handoff_path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    return (project_root / candidate).resolve()


def resolve_existing_handoff_path(project_root: Path) -> tuple[Path, str]:
    for relative_path in RECOGNIZED_RELATIVE_PATHS:
        candidate = project_root / relative_path
        if candidate.exists():
            return candidate.resolve(), "existing"
    return (project_root / DEFAULT_RELATIVE_PATH).resolve(), "default"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve the canonical repo-local HANDOFF path for a project."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Repository or project root used for detection. Defaults to the current directory.",
    )
    parser.add_argument(
        "--handoff-path",
        help="Explicit repo-local or absolute HANDOFF path. Relative paths are resolved from the project root.",
    )
    parser.add_argument(
        "--ensure",
        action="store_true",
        help="Create the directory and initialize the file when missing.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format. Defaults to text.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    project_root = canonical_project_root(Path(args.project_root).expanduser().resolve())
    if args.handoff_path:
        handoff_path = resolve_explicit_handoff_path(project_root, args.handoff_path)
        resolution_source = "explicit"
    else:
        handoff_path, resolution_source = resolve_existing_handoff_path(project_root)

    if args.ensure:
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        if not handoff_path.exists():
            handoff_path.write_text(INITIAL_CONTENT, encoding="utf-8")

    payload = {
        "project_root": str(project_root),
        "handoff_path": str(handoff_path),
        "resolution_source": resolution_source,
        "exists": handoff_path.exists(),
    }

    if args.format == "json":
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(handoff_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
