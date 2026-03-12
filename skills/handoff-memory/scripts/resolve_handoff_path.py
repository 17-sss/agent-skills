#!/usr/bin/env python3
"""Resolve a canonical repo-local or workspace-local handoff path."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_DOCUMENTS = {
    "handoff": (
        (Path("docs") / "HANDOFF.md", Path("memories") / "HANDOFF.md", Path("HANDOFF.md")),
        Path("docs") / "HANDOFF.md",
    ),
}
WORKSPACE_ROOT = Path("_memory")
WORKSPACE_DOCUMENTS = {
    "handoff": (Path("HANDOFF.md"), """# HANDOFF

## Metadata

- Workspace:
- Root:
- Last Updated:
- Updated By:

## Current Objective

## Current State

## Repo Impact

- Repositories involved:
- Cross-repo dependencies:
- Shared blockers:

## Changes Made

## Validation

- Checks run:
- Results:
- Not run yet:

## Open Questions / Risks

## Next Actions

1.

## Resume Prompt

Continue this workspace from the shared HANDOFF document. First verify the involved repositories still match the notes, then execute the next action.
"""),
    "workspace": (Path("WORKSPACE.md"), """# WORKSPACE

## Overview

- Workspace:
- Root:
- Purpose:

## Repositories

- Repo:
- Repo:

## Shared Commands

- Install:
- Dev:
- Test:

## Ownership / Boundaries

- Frontend:
- Backend:
- Infra:

## Environment Notes

- Shared services:
- Required tools:
- Local assumptions:
"""),
    "decisions": (Path("DECISIONS.md"), """# DECISIONS

## Decision Log

### YYYY-MM-DD - Title

- Status:
- Context:
- Decision:
- Consequences:
- Affected repositories:
"""),
    "patterns": (Path("PATTERNS.md"), """# PATTERNS

## Reusable Patterns

### Pattern Name

- Problem:
- Recommended approach:
- Example repositories:
- Notes:
"""),
}
REPO_INITIAL_CONTENT = """# HANDOFF

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


def detect_scope(project_root: Path) -> str:
    if run_git(project_root, "rev-parse", "--show-toplevel"):
        return "repo"

    child_git_dirs = [
        child for child in project_root.iterdir()
        if child.is_dir() and (child / ".git").exists()
    ]
    if len(child_git_dirs) >= 2:
        return "workspace"
    if (project_root / WORKSPACE_ROOT).exists():
        return "workspace"
    return "repo"


def resolve_existing_repo_handoff_path(project_root: Path) -> tuple[Path, str]:
    recognized_paths, default_path = REPO_DOCUMENTS["handoff"]
    for relative_path in recognized_paths:
        candidate = project_root / relative_path
        if candidate.exists():
            return candidate.resolve(), "existing"
    return (project_root / default_path).resolve(), "default"


def workspace_relative_path(document: str, root: Path) -> Path:
    relative_name, _ = WORKSPACE_DOCUMENTS[document]
    return root / relative_name


def resolve_workspace_document_path(project_root: Path, document: str) -> tuple[Path, str]:
    candidate = project_root / workspace_relative_path(document, WORKSPACE_ROOT)
    if candidate.exists():
        return candidate.resolve(), "existing"
    return candidate.resolve(), "default"


def initial_content_for(scope: str, document: str) -> str:
    if scope == "workspace":
        return WORKSPACE_DOCUMENTS[document][1]
    return REPO_INITIAL_CONTENT


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resolve the canonical repo-local or workspace-local memory path."
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Repository or project root used for detection. Defaults to the current directory.",
    )
    parser.add_argument(
        "--scope",
        choices=("auto", "repo", "workspace"),
        default="auto",
        help="Memory scope. Defaults to auto.",
    )
    parser.add_argument(
        "--document",
        choices=("handoff", "workspace", "decisions", "patterns"),
        default="handoff",
        help="Document type. Workspace-only documents require --scope workspace or auto-detected workspace.",
    )
    parser.add_argument(
        "--handoff-path",
        help="Explicit repo-local or absolute HANDOFF path. Relative paths are resolved from the project root.",
    )
    parser.add_argument(
        "--ensure",
        action="store_true",
        help="Create the file when missing.",
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

    raw_project_root = Path(args.project_root).expanduser().resolve()
    detected_scope = detect_scope(raw_project_root)
    scope = detected_scope if args.scope == "auto" else args.scope
    project_root = (
        canonical_project_root(raw_project_root)
        if scope == "repo"
        else raw_project_root
    )

    if scope == "repo" and args.document != "handoff":
        parser.error("Repo scope only supports --document handoff.")

    if args.handoff_path:
        handoff_path = resolve_explicit_handoff_path(project_root, args.handoff_path)
        resolution_source = "explicit"
    else:
        if scope == "workspace":
            handoff_path, resolution_source = resolve_workspace_document_path(
                project_root, args.document
            )
        else:
            handoff_path, resolution_source = resolve_existing_repo_handoff_path(project_root)

    if args.ensure:
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        if not handoff_path.exists():
            handoff_path.write_text(initial_content_for(scope, args.document), encoding="utf-8")

    payload = {
        "project_root": str(project_root),
        "scope": scope,
        "detected_scope": detected_scope,
        "document": args.document,
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
