#!/usr/bin/env python3
"""Non-destructively bootstrap godot-dev-loop files into a Godot 4 project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "bootstrap"
PRESERVE_STATE_PATHS = {
    Path("docs/STATUS.md"),
    Path("docs/feedback/INBOX.md"),
}
EXECUTABLE_TARGETS = {
    Path("loop/loop.sh"),
    Path("loop/runners/claude.sh"),
    Path("loop/runners/codex.sh"),
    Path("scripts/game-capture.sh"),
    Path("scripts/validate-game-design.py"),
    Path("qa/visual-qa/godot/resolve_game_state.py"),
}
REQUIRED_DESIGN_HEADINGS = (
    "Game Concept",
    "Core Gameplay Loop",
    "Good Enough / Stop Criteria",
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\b(?:TODO|TBD)\b", re.IGNORECASE),
    re.compile(r"\?\?\?"),
    re.compile(r"\[\s*(?:fill|answer|replace)[^\]]*\]", re.IGNORECASE),
    re.compile(r"<\s*(?:fill|answer|replace)[^>]*>", re.IGNORECASE),
)
IGNORE_BLOCK = """# godot-dev-loop transient state
/artifacts/visual/
/loop/logs/
/loop/STOP
/loop/BLOCKED
# end godot-dev-loop transient state
"""


class BootstrapError(RuntimeError):
    pass


def compact(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.split())
    return normalized or None


def section_body(text: str, heading: str) -> str | None:
    match = re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", text)
    if match is None:
        return None
    remainder = text[match.end() :]
    next_heading = re.search(r"(?m)^##\s+", remainder)
    return remainder[: next_heading.start() if next_heading else len(remainder)].strip()


def design_errors(text: str) -> list[str]:
    errors: list[str] = []
    for heading in REQUIRED_DESIGN_HEADINGS:
        body = section_body(text, heading)
        if body is None:
            errors.append(f"missing ## {heading}")
        elif not body:
            errors.append(f"empty ## {heading}")
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(text):
            errors.append(f"unresolved placeholder {pattern.pattern!r}")
    return errors


def build_design(args: argparse.Namespace) -> str:
    game = compact(args.game)
    core_loop = compact(args.core_loop)
    good_enough = compact(args.good_enough)
    missing = [
        flag
        for flag, value in (
            ("--game", game),
            ("--core-loop", core_loop),
            ("--good-enough", good_enough),
        )
        if value is None
    ]
    if missing:
        raise BootstrapError(
            "docs/DESIGN.md is missing; answer the brief gate and provide "
            + ", ".join(missing)
        )

    fantasy = compact(args.player_fantasy) or (
        "Use the concept and core loop as the intended experience; no narrower player fantasy was specified."
    )
    slice_target = compact(args.slice_target) or (
        "A playable slice that demonstrates the complete core gameplay loop and meets the stop criteria below."
    )
    visual_direction = compact(args.visual_direction) or (
        "No separate visual direction is fixed; preserve the project's existing visual language and explicit future user decisions."
    )
    constraints = compact(args.constraints) or (
        "Godot 4.x is the v1 runtime for visual QA. Preserve existing repository and platform constraints."
    )
    non_goals = compact(args.non_goals) or (
        "Do not expand beyond the current playable slice unless a later human directive changes this contract."
    )

    return f"""# Game Design

## Game Concept

{game}

## Player Fantasy / Intended Experience

{fantasy}

## Core Gameplay Loop

{core_loop}

## Current Playable-Slice Target

{slice_target}

## Visual Direction

{visual_direction}

## Constraints

{constraints}

## Non-Goals

{non_goals}

## Good Enough / Stop Criteria

{good_enough}

## Material User Decisions

- Game: {game}
- Core loop: {core_loop}
- Stop condition: {good_enough}
"""


def template_files() -> dict[Path, bytes]:
    if not TEMPLATE_ROOT.is_dir():
        raise BootstrapError(f"bundled template directory is missing: {TEMPLATE_ROOT}")
    return {
        path.relative_to(TEMPLATE_ROOT): path.read_bytes()
        for path in sorted(TEMPLATE_ROOT.rglob("*"))
        if path.is_file()
    }


def preflight_gitignore(project_root: Path) -> tuple[bool, str]:
    path = project_root / ".gitignore"
    if not path.exists():
        return True, "create"
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise BootstrapError(f"cannot read existing .gitignore: {exc}") from exc
    marker = "# godot-dev-loop transient state"
    if marker not in text:
        return True, "append"
    if IGNORE_BLOCK.strip() in text:
        return False, "unchanged"
    raise BootstrapError(
        "existing .gitignore contains a conflicting godot-dev-loop block; resolve it manually"
    )


def find_git_root(project_root: Path) -> Path | None:
    if shutil.which("git") is None:
        raise BootstrapError("git is required but was not found in PATH")
    result = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        root = result.stdout.strip()
        if not root:
            raise BootstrapError("git rev-parse succeeded without returning a repository root")
        return Path(root).resolve()
    details = (result.stderr or result.stdout).strip()
    if "not a git repository" in details.lower():
        return None
    raise BootstrapError(
        "cannot determine whether the project is already inside Git; refusing to initialize "
        f"a possibly nested repository: {details or 'git rev-parse failed'}"
    )


def initialize_git(project_root: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(project_root), "init"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        details = (result.stderr or result.stdout).strip()
        raise BootstrapError(f"git init failed: {details}")
    git_root = find_git_root(project_root)
    if git_root is None:
        raise BootstrapError("git init returned success but no worktree/repository was detected")
    return git_root


def append_gitignore(project_root: Path, action: str) -> None:
    if action == "unchanged":
        return
    path = project_root / ".gitignore"
    prefix = b""
    if action == "append":
        prefix = path.read_bytes()
        if prefix and not prefix.endswith(b"\n"):
            prefix += b"\n"
        if prefix and not prefix.endswith(b"\n\n"):
            prefix += b"\n"
    path.write_bytes(prefix + IGNORE_BLOCK.encode("utf-8"))


def bootstrap(args: argparse.Namespace) -> dict[str, object]:
    project_root = args.project.resolve()
    if not project_root.is_dir():
        raise BootstrapError(f"target project directory does not exist: {project_root}")
    if not (project_root / "project.godot").is_file():
        raise BootstrapError(
            f"target is not a Godot project because project.godot is missing: {project_root}"
        )

    design_path = project_root / "docs" / "DESIGN.md"
    if design_path.exists():
        if not args.accept_existing_design:
            raise BootstrapError(
                "docs/DESIGN.md already exists and will not be overwritten; inspect it and rerun with --accept-existing-design"
            )
        try:
            existing_design = design_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise BootstrapError(f"cannot read existing docs/DESIGN.md: {exc}") from exc
        errors = design_errors(existing_design)
        if errors:
            raise BootstrapError(
                "existing docs/DESIGN.md is not loop-ready: " + "; ".join(errors)
            )
        generated_design: bytes | None = None
    else:
        generated_design = build_design(args).encode("utf-8")

    files = template_files()
    if generated_design is not None:
        files[Path("docs/DESIGN.md")] = generated_design

    conflicts: list[str] = []
    preserved: list[str] = []
    unchanged: list[str] = []
    for relative, content in files.items():
        destination = project_root / relative
        if not destination.exists():
            continue
        if relative in PRESERVE_STATE_PATHS or relative == Path("docs/DESIGN.md"):
            if not destination.is_file():
                conflicts.append(f"{relative.as_posix()} exists and is not a regular file")
                continue
            preserved.append(relative.as_posix())
            continue
        if not destination.is_file():
            conflicts.append(f"{relative.as_posix()} exists and is not a regular file")
            continue
        try:
            existing = destination.read_bytes()
        except OSError as exc:
            conflicts.append(f"{relative.as_posix()} cannot be read: {exc}")
            continue
        if existing == content:
            unchanged.append(relative.as_posix())
        else:
            conflicts.append(f"{relative.as_posix()} differs from the bundled file")
    if conflicts:
        raise BootstrapError(
            "bootstrap conflicts detected; no workflow files were written: "
            + "; ".join(conflicts)
        )

    _, gitignore_action = preflight_gitignore(project_root)
    existing_git_root = find_git_root(project_root)
    if existing_git_root is None:
        git_root = initialize_git(project_root)
        git_action = "initialized"
    else:
        git_root = existing_git_root
        git_action = "reused"

    created: list[str] = []
    for relative, content in sorted(files.items(), key=lambda item: item[0].as_posix()):
        destination = project_root / relative
        if destination.exists():
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
        if relative in EXECUTABLE_TARGETS:
            destination.chmod(destination.stat().st_mode | 0o755)
        created.append(relative.as_posix())

    (project_root / "artifacts" / "visual").mkdir(parents=True, exist_ok=True)
    (project_root / "loop" / "logs").mkdir(parents=True, exist_ok=True)
    append_gitignore(project_root, gitignore_action)

    return {
        "project_root": str(project_root),
        "git_action": git_action,
        "git_root": str(git_root),
        "gitignore": gitignore_action,
        "created": created,
        "preserved": sorted(set(preserved)),
        "unchanged": sorted(set(unchanged)),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path)
    parser.add_argument("--game")
    parser.add_argument("--core-loop")
    parser.add_argument("--good-enough")
    parser.add_argument("--player-fantasy")
    parser.add_argument("--slice-target")
    parser.add_argument("--visual-direction")
    parser.add_argument("--constraints")
    parser.add_argument("--non-goals")
    parser.add_argument(
        "--accept-existing-design",
        action="store_true",
        help="Assert that the existing canonical DESIGN already answers the brief gate.",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = bootstrap(args)
    except BootstrapError as exc:
        print(f"godot-dev-loop bootstrap failed: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"godot-dev-loop bootstrapped: {result['project_root']}")
        print(f"git: {result['git_action']} {result['git_root']}")
        print(f"created: {len(result['created'])}")
        print(f"preserved: {len(result['preserved'])}")
        print("next: run GAME_START=smoke ./scripts/game-capture.sh and inspect the PNG")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
