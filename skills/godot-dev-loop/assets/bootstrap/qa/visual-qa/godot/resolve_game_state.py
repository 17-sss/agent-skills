#!/usr/bin/env python3
"""Resolve a GAME_START alias or direct Godot scene path deterministically."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from typing import NoReturn


ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
SCENE_SUFFIXES = {".tscn", ".scn"}


def fail(message: str) -> NoReturn:
    raise ValueError(message)


def validate_scene_path(project_root: Path, scene: str) -> Path:
    if "\t" in scene or "\n" in scene or "\r" in scene:
        fail("scene paths cannot contain tabs or newlines")
    if not scene.startswith("res://"):
        fail(f"scene path must start with res://, got {scene!r}")
    relative = scene.removeprefix("res://")
    if not relative:
        fail("scene path cannot be res:// alone")
    resolved = (project_root / relative).resolve()
    try:
        resolved.relative_to(project_root)
    except ValueError:
        fail(f"scene path escapes the project: {scene}")
    if resolved.suffix.lower() not in SCENE_SUFFIXES:
        fail(f"scene path must end in .tscn or .scn: {scene}")
    if not resolved.is_file():
        fail(f"scene does not exist: {scene}")
    return resolved


def load_registry(registry_path: Path) -> dict[str, str]:
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read state registry {registry_path}: {exc}")
    if not isinstance(raw, dict):
        fail("state registry must be a JSON object")
    registry: dict[str, str] = {}
    for alias, scene in raw.items():
        if not isinstance(alias, str) or not ALIAS_PATTERN.fullmatch(alias):
            fail(f"invalid state alias: {alias!r}")
        if not isinstance(scene, str):
            fail(f"state alias {alias!r} must map to a string scene path")
        registry[alias] = scene
    return registry


def artifact_stem(requested: str, scene: str) -> str:
    if ALIAS_PATTERN.fullmatch(requested):
        return requested.lower()
    base = Path(scene.removeprefix("res://")).stem
    slug = re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-") or "scene"
    digest = hashlib.sha256(scene.encode("utf-8")).hexdigest()[:8]
    return f"scene-{slug}-{digest}"


def resolve(project_root: Path, requested: str) -> tuple[str, str, str]:
    if not requested or "\t" in requested or "\n" in requested or "\r" in requested:
        fail("GAME_START must be one non-empty alias or res:// scene path")
    registry_path = project_root / "qa" / "visual-qa" / "godot" / "states.json"
    registry = load_registry(registry_path)
    if requested.startswith("res://"):
        scene = requested
    else:
        if not ALIAS_PATTERN.fullmatch(requested):
            fail(f"invalid GAME_START alias: {requested!r}")
        if requested not in registry:
            known = ", ".join(sorted(registry)) or "none"
            fail(f"unknown GAME_START alias {requested!r}; known aliases: {known}")
        scene = registry[requested]
    validate_scene_path(project_root, scene)
    return requested, scene, artifact_stem(requested, scene)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--state", required=True)
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    try:
        requested, scene, stem = resolve(project_root, args.state)
    except ValueError as exc:
        print(f"godot-dev-loop: {exc}", file=sys.stderr)
        return 2
    print("\t".join((requested, scene, stem)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
