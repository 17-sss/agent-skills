#!/usr/bin/env python3
"""Validate Codex-native workflow skills and optionally check upstream drift."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
from urllib.request import urlopen
from urllib.parse import urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = (
    "spec-interview",
    "reviewed-plan",
    "completion-loop",
    "visual-match",
    "review-gate",
    "milestone-runner",
)
OPTIONAL_HANDOFF_HEADING = "## Offer an optional next workflow"
OPTIONAL_HANDOFFS = {
    "spec-interview": (
        "reviewed-plan",
        "completion-loop",
        "milestone-runner",
    ),
    "reviewed-plan": (
        "completion-loop",
        "milestone-runner",
    ),
}
OPTIONAL_HANDOFF_MARKERS = (
    "Keep this package complete on its own.",
    "Do not invoke or activate another skill.",
    "current Codex task's available-skill inventory",
    "Do not inspect the filesystem",
    "Do not install a missing skill.",
    "If the inventory is unavailable, treat every downstream skill as unavailable.",
    "Do not mention unavailable skills.",
    "the user explicitly chooses and invokes",
    "Offer at most one recommendation",
    "Omit this section",
    "Do not substitute a weaker route merely because the best-fit skill is unavailable.",
    "Render the recommendation as a copyable invocation",
)
OPTIONAL_HANDOFF_READINESS_MARKERS = {
    "spec-interview": (
        "only after the readiness gate has passed",
        "no remaining decision could materially change implementation direction or acceptance",
    ),
    "reviewed-plan": (
        "Architect returned `ACCEPT`",
        "Critic returned `APPROVE` for the same plan revision",
        "the handoff is `NOT APPROVED`",
    ),
}
HARD_HANDOFF_PATTERNS = {
    "mandatory sequencing": re.compile(r"(?i)\bbefore continuing\b"),
    "mandatory invocation": re.compile(
        r"(?i)\b(?:must|required to) (?:run|invoke|install|use|have)\b"
    ),
    "automatic activation": re.compile(
        r"(?i)\bautomatically (?:invoke|run|activate)\b"
    ),
    "required dependency": re.compile(
        r"(?i)\b(?:cannot|can't) continue without\b"
    ),
}
OTHER_SKILL_NAMES = (
    "design-loop",
    "handoff-memory",
    "github-pr-review",
    "github-pr-publish",
    "commit-helper",
)
STATE_DIRECTORY = ".agent-workflows"
SOURCE_MANIFEST = REPO_ROOT / "docs" / "native-workflow-sources.json"
ROOT_README = REPO_ROOT / "README.md"
KOREAN_README = REPO_ROOT / "README.ko.md"
TUI_GROUP_MANIFEST = REPO_ROOT / ".claude-plugin" / "marketplace.json"
ALLOWED_REFERENCE_HOSTS = {
    "developers.openai.com",
    "github.com",
    "learn.chatgpt.com",
    "playwright.dev",
}
REQUIRED_CODEX_CAPABILITIES = {
    "Plan mode and /plan",
    "Goal mode and /goal",
    "native /review target selection and read-only review behavior",
    "non-interactive codex review targeting",
    "native subagents",
    "skills and plugins",
    "built-in Browser and Chrome extension routing",
    "image input and image generation",
}
BANNED_PATTERNS = {
    "legacy workflow provenance": re.compile(r"(?i)\boh-my-codex\b|yeachan-heo"),
    "runtime name": re.compile(r"(?i)(?:^|[^a-z])omx(?:[^a-z]|$)"),
    "runtime state path": re.compile(r"(?i)\.omx(?:/|\b)"),
    "terminal multiplexer": re.compile(r"(?i)\btmux\b"),
    "runtime display": re.compile(r"(?i)\bhud\b"),
    "external advisor shim": re.compile(r"(?i)\bask_codex\b"),
    "parallel runtime wrapper": re.compile(r"(?i)\bultrawork\b"),
    "runtime stop hook": re.compile(r"(?i)\bstop[- ]hook\b"),
    "runtime lifecycle hook": re.compile(
        r"(?i)\b(?:userpromptsubmit|pretooluse|posttooluse|sessionstart|sessionend|"
        r"subagentstart|subagentstop|precompact|permissionrequest|taskcompleted)\b|"
        r"(?:^|[^a-z])hooks?(?:/|\b)"
    ),
}
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)
    print(f"FAIL {message}")


def validate_frontmatter(skill_dir: Path, errors: list[str]) -> None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        fail(f"{skill_file.relative_to(REPO_ROOT)} is missing", errors)
        return

    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail(f"{skill_file.relative_to(REPO_ROOT)} has no opening frontmatter", errors)
        return

    try:
        closing = lines.index("---", 1)
    except ValueError:
        fail(f"{skill_file.relative_to(REPO_ROOT)} has no closing frontmatter", errors)
        return

    fields: dict[str, str] = {}
    keys: list[str] = []
    for line in lines[1:closing]:
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            key, value = match.groups()
            keys.append(key)
            fields[key] = value.strip()
    if keys != ["name", "description"]:
        fail(
            f"{skill_file.relative_to(REPO_ROOT)} frontmatter keys are {keys}, expected name and description",
            errors,
        )

    expected_name = skill_dir.name
    if fields.get("name") != expected_name:
        fail(f"{skill_file.relative_to(REPO_ROOT)} name does not match its directory", errors)

    if "TODO" in text:
        fail(f"{skill_file.relative_to(REPO_ROOT)} still contains TODO text", errors)


def validate_runtime_independence(skill_dir: Path, errors: list[str]) -> None:
    if skill_dir.is_symlink():
        fail(f"{skill_dir.relative_to(REPO_ROOT)} is a symlink; skill packages must be self-contained", errors)
        return
    if not skill_dir.is_dir():
        return

    for path in sorted(skill_dir.rglob("*")):
        if path.is_symlink():
            fail(f"{path.relative_to(REPO_ROOT)} is a symlink; skill packages must be self-contained", errors)
            continue
        if not path.is_file():
            continue
        try:
            raw = path.read_bytes()
            if b"\0" in raw:
                continue
            text = raw.decode("utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for label, pattern in BANNED_PATTERNS.items():
            if pattern.search(text):
                fail(f"{path.relative_to(REPO_ROOT)} contains banned {label}", errors)


def validate_standalone_package(skill_dir: Path, errors: list[str]) -> None:
    """Reject sibling dependencies while allowing guarded, optional handoffs."""
    if not skill_dir.is_dir():
        return
    skill_file = skill_dir / "SKILL.md"
    skill_text = ""
    if skill_file.is_file() and not skill_file.is_symlink():
        try:
            skill_text = skill_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pass

    handoff_span: tuple[int, int] | None = None
    expected_handoffs = OPTIONAL_HANDOFFS.get(skill_dir.name)
    heading_matches = list(
        re.finditer(
            rf"(?m)^{re.escape(OPTIONAL_HANDOFF_HEADING)}\s*$",
            skill_text,
        )
    )
    if expected_handoffs is None:
        if heading_matches:
            fail(
                f"{skill_file.relative_to(REPO_ROOT)} declares an optional handoff section "
                "outside the strict allowlist",
                errors,
            )
    elif len(heading_matches) != 1:
        fail(
            f"{skill_file.relative_to(REPO_ROOT)} must contain exactly one "
            f"{OPTIONAL_HANDOFF_HEADING!r} section",
            errors,
        )
    else:
        start = heading_matches[0].start()
        next_heading = re.search(r"(?m)^##\s+", skill_text[heading_matches[0].end() :])
        end = (
            heading_matches[0].end() + next_heading.start()
            if next_heading
            else len(skill_text)
        )
        handoff_span = (start, end)
        handoff_text = skill_text[start:end]
        required_markers = (
            *OPTIONAL_HANDOFF_MARKERS,
            *OPTIONAL_HANDOFF_READINESS_MARKERS[skill_dir.name],
        )
        for marker in required_markers:
            if marker not in handoff_text:
                fail(
                    f"{skill_file.relative_to(REPO_ROOT)} optional handoff lacks guardrail "
                    f"{marker!r}",
                    errors,
                )
        for downstream in expected_handoffs:
            if f"`${downstream}`" not in handoff_text:
                fail(
                    f"{skill_file.relative_to(REPO_ROOT)} optional handoff does not document "
                    f"allowed route {downstream}",
                    errors,
                )
        for label, pattern in HARD_HANDOFF_PATTERNS.items():
            if pattern.search(handoff_text):
                fail(
                    f"{skill_file.relative_to(REPO_ROOT)} optional handoff contains {label}",
                    errors,
                )

    other_names = [name for name in SKILL_NAMES if name != skill_dir.name]
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for other_name in other_names:
            pattern = re.compile(
                rf"(?<![a-z0-9-])\$?{re.escape(other_name)}(?![a-z0-9-])",
                re.IGNORECASE,
            )
            for match in pattern.finditer(text):
                allowed_optional_reference = (
                    path == skill_file
                    and handoff_span is not None
                    and expected_handoffs is not None
                    and other_name in expected_handoffs
                    and handoff_span[0] <= match.start() < handoff_span[1]
                )
                if not allowed_optional_reference:
                    fail(
                        f"{path.relative_to(REPO_ROOT)} references sibling skill {other_name}; "
                        "every package must install and run independently",
                        errors,
                    )


def validate_bundled_scripts(skill_dir: Path, errors: list[str]) -> None:
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return
    for script in sorted(scripts_dir.iterdir()):
        if script.is_file() and not script.is_symlink() and not os.access(script, os.X_OK):
            fail(f"{script.relative_to(REPO_ROOT)} must be executable", errors)


def validate_state_contract(skill_dir: Path, errors: list[str]) -> None:
    if not skill_dir.is_dir():
        return
    surfaces: dict[Path, str] = {}
    for path in sorted(skill_dir.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            surfaces[path] = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    if skill_dir.name != "milestone-runner":
        for path, text in surfaces.items():
            if STATE_DIRECTORY in text:
                fail(
                    f"{path.relative_to(REPO_ROOT)} creates unnecessary shared workflow state; "
                    "only milestone-runner may use it",
                    errors,
                )
        return

    required_markers = {
        skill_dir / "SKILL.md": (
            ".agent-workflows/goals/<slug>/",
            "pending transaction",
        ),
        skill_dir / "references" / "state-contract.md": (
            ".agent-workflows/",
            ".init.lock",
            ".pending-transaction.json",
            "implementation_changed",
        ),
        skill_dir / "scripts" / "goal_state.py": (
            'STATE_DIRECTORY = ".agent-workflows"',
            'TRANSACTION_FILE = ".pending-transaction.json"',
            "rename_directory_noreplace",
            "validate_projection",
        ),
    }
    for path, markers in required_markers.items():
        text = surfaces.get(path)
        if text is None:
            fail(f"{path.relative_to(REPO_ROOT)} is missing or unreadable", errors)
            continue
        for marker in markers:
            if marker not in text:
                fail(
                    f"{path.relative_to(REPO_ROOT)} lacks state-contract marker {marker!r}",
                    errors,
                )
        if re.search(r"\.codex/[^\n]*\.agent-workflows", text, re.IGNORECASE):
            fail(
                f"{path.relative_to(REPO_ROOT)} nests mutable state under .codex",
                errors,
            )
    script_text = surfaces.get(skill_dir / "scripts" / "goal_state.py", "")
    for native_goal_call in ("create_goal", "get_goal", "update_goal"):
        if native_goal_call in script_text:
            fail(
                f"{skill_dir.name} helper must not call native goal tool {native_goal_call}",
                errors,
            )
    try:
        script_tree = ast.parse(script_text)
    except SyntaxError as exc:
        fail(f"{skill_dir.name} helper is not valid Python: {exc}", errors)
        return
    string_literals = {
        node.value
        for node in ast.walk(script_tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }
    forbidden_state_literals = {
        literal
        for literal in string_literals
        if literal.startswith((".codex", ".omx", "~/", "/home/", "/Users/"))
        or "CODEX_HOME" in literal
    }
    if forbidden_state_literals:
        fail(
            f"{skill_dir.name} helper contains alternate mutable state roots: "
            f"{sorted(forbidden_state_literals)}",
            errors,
        )
    if "__file__" in script_text:
        fail(
            f"{skill_dir.name} helper must not store state relative to its installation path",
            errors,
        )


def validate_links(skill_dir: Path, errors: list[str]) -> None:
    for path in skill_dir.rglob("*.md"):
        validate_markdown_links(path, errors, allowed_root=skill_dir)


def validate_markdown_links(
    path: Path,
    errors: list[str],
    allowed_root: Path,
) -> None:
    text = path.read_text(encoding="utf-8")
    resolved_root = allowed_root.resolve()
    for target in MARKDOWN_LINK.findall(text):
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        clean_target = target.split("#", 1)[0]
        resolved = (path.parent / clean_target).resolve()
        try:
            resolved.relative_to(resolved_root)
        except ValueError:
            fail(
                f"{path.relative_to(REPO_ROOT)} links outside its installable root: {clean_target}",
                errors,
            )
            continue
        if not resolved.exists():
            fail(
                f"{path.relative_to(REPO_ROOT)} links to missing {clean_target}",
                errors,
            )


def validate_catalog_files(skill_dir: Path, errors: list[str]) -> None:
    metadata_path = skill_dir / "metadata.json"
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{metadata_path.relative_to(REPO_ROOT)} is invalid: {exc}", errors)
    else:
        if metadata.get("name") != skill_dir.name:
            fail(f"{metadata_path.relative_to(REPO_ROOT)} name mismatch", errors)
        required_types = {
            "name": str,
            "version": str,
            "organization": str,
            "date": str,
            "abstract": str,
            "references": list,
        }
        if set(metadata) != set(required_types):
            fail(
                f"{metadata_path.relative_to(REPO_ROOT)} keys must be {sorted(required_types)}",
                errors,
            )
        for key, expected_type in required_types.items():
            value = metadata.get(key)
            if not isinstance(value, expected_type) or (
                isinstance(value, str) and not value.strip()
            ):
                fail(
                    f"{metadata_path.relative_to(REPO_ROOT)} {key} must be a non-empty {expected_type.__name__}",
                    errors,
                )
        if isinstance(metadata.get("version"), str) and not re.fullmatch(
            r"\d+\.\d+\.\d+", metadata["version"]
        ):
            fail(f"{metadata_path.relative_to(REPO_ROOT)} version must be semantic", errors)
        references = metadata.get("references")
        if isinstance(references, list):
            if not references:
                fail(f"{metadata_path.relative_to(REPO_ROOT)} references cannot be empty", errors)
            for reference in references:
                if not isinstance(reference, str):
                    fail(f"{metadata_path.relative_to(REPO_ROOT)} has a non-string reference", errors)
                    continue
                parsed = urlparse(reference)
                if parsed.scheme != "https" or parsed.netloc not in ALLOWED_REFERENCE_HOSTS:
                    fail(
                        f"{metadata_path.relative_to(REPO_ROOT)} has unsupported reference {reference}",
                        errors,
                    )

    openai_path = skill_dir / "agents" / "openai.yaml"
    try:
        openai_text = openai_path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"{openai_path.relative_to(REPO_ROOT)} is missing: {exc}", errors)
        return

    lines = openai_text.splitlines()
    expected_prefixes = (
        "interface:",
        "  display_name: ",
        "  short_description: ",
        "  default_prompt: ",
        "policy:",
        "  allow_implicit_invocation: false",
    )
    if len(lines) != len(expected_prefixes):
        fail(f"{openai_path.relative_to(REPO_ROOT)} has an unexpected YAML shape", errors)
        return
    for line, prefix in zip(lines, expected_prefixes):
        if line == prefix or (
            prefix.endswith(" ") and line.startswith(prefix)
        ):
            continue
        fail(f"{openai_path.relative_to(REPO_ROOT)} expected line prefix {prefix!r}", errors)
        return

    parsed_interface: dict[str, str] = {}
    for key, line in zip(
        ("display_name", "short_description", "default_prompt"),
        lines[1:4],
    ):
        raw_value = line.split(": ", 1)[1]
        try:
            value = json.loads(raw_value)
        except json.JSONDecodeError:
            fail(f"{openai_path.relative_to(REPO_ROOT)} {key} must be a quoted string", errors)
            continue
        if not isinstance(value, str) or not value.strip():
            fail(f"{openai_path.relative_to(REPO_ROOT)} {key} must be non-empty", errors)
            continue
        parsed_interface[key] = value

    default_prompt = parsed_interface.get("default_prompt", "")
    if f"${skill_dir.name}" not in default_prompt:
        fail(f"{openai_path.relative_to(REPO_ROOT)} default prompt lacks ${skill_dir.name}", errors)

    short_description = parsed_interface.get("short_description", "")
    if short_description and not 25 <= len(short_description) <= 64:
        fail(
            f"{openai_path.relative_to(REPO_ROOT)} short_description must be 25-64 characters",
            errors,
        )


def validate_root_catalog(errors: list[str]) -> None:
    catalogs: dict[Path, str] = {}
    for path in (ROOT_README, KOREAN_README):
        try:
            catalogs[path] = path.read_text(encoding="utf-8")
        except OSError as exc:
            fail(f"{path.relative_to(REPO_ROOT)} is missing: {exc}", errors)

    for path, readme in catalogs.items():
        for name in SKILL_NAMES:
            if f"### {name}" not in readme:
                fail(f"{path.name} lacks catalog heading for {name}", errors)
            if f"${name}" not in readme:
                fail(f"{path.name} lacks invocation for ${name}", errors)
        validate_markdown_links(path, errors, allowed_root=REPO_ROOT)

    english = catalogs.get(ROOT_README, "")
    korean = catalogs.get(KOREAN_README, "")
    if "[한국어](README.ko.md)" not in english:
        fail("README.md lacks the Korean language link", errors)
    if "[English](README.md)" not in korean:
        fail("README.ko.md lacks the English language link", errors)


def validate_tui_group_manifest(errors: list[str]) -> None:
    try:
        manifest = json.loads(TUI_GROUP_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{TUI_GROUP_MANIFEST.relative_to(REPO_ROOT)} is invalid: {exc}", errors)
        return

    if not isinstance(manifest, dict):
        fail(f"{TUI_GROUP_MANIFEST.relative_to(REPO_ROOT)} must contain a JSON object", errors)
        return
    plugins = manifest.get("plugins")
    if not isinstance(plugins, list) or not all(isinstance(item, dict) for item in plugins):
        fail(
            f"{TUI_GROUP_MANIFEST.relative_to(REPO_ROOT)} plugins must be a list of objects",
            errors,
        )
        return
    group_names = [item.get("name") for item in plugins]
    if not all(isinstance(name, str) for name in group_names):
        fail(f"{TUI_GROUP_MANIFEST.relative_to(REPO_ROOT)} group names must be strings", errors)
        return

    expected_groups = {
        "codex": {f"./skills/{name}" for name in SKILL_NAMES},
        "other": {f"./skills/{name}" for name in OTHER_SKILL_NAMES},
    }
    groups = {item.get("name"): item for item in plugins}
    if set(groups) != set(expected_groups) or len(groups) != len(plugins):
        fail(
            f"{TUI_GROUP_MANIFEST.relative_to(REPO_ROOT)} groups must be exactly codex and other",
            errors,
        )
        return

    all_grouped_paths: list[str] = []
    for group_name, expected_paths in expected_groups.items():
        group = groups[group_name]
        grouped_paths = group.get("skills")
        if group.get("source") != "./":
            fail(f"TUI group {group_name} source must be ./", errors)
        if (
            not isinstance(grouped_paths, list)
            or not all(isinstance(path, str) for path in grouped_paths)
            or len(grouped_paths) != len(set(grouped_paths))
            or set(grouped_paths) != expected_paths
        ):
            fail(
                f"TUI group {group_name} must exactly match its inventory: "
                f"{sorted(expected_paths)}",
                errors,
            )
            continue
        all_grouped_paths.extend(grouped_paths)

    if len(all_grouped_paths) != len(set(all_grouped_paths)):
        fail("TUI groups must not contain the same skill more than once", errors)
    for relative_path in all_grouped_paths:
        skill_dir = REPO_ROOT / relative_path.removeprefix("./")
        if not (skill_dir / "SKILL.md").is_file():
            fail(f"{relative_path} does not point to an installable skill", errors)


def find_skill_validator(explicit: str | None = None) -> Path | None:
    override = explicit or os.environ.get("SKILL_VALIDATOR")
    if override:
        candidate = Path(override).expanduser()
        return candidate if candidate.is_file() else None
    codex_root = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
    candidate = (
        codex_root
        / "skills"
        / ".system"
        / "skill-creator"
        / "scripts"
        / "quick_validate.py"
    )
    return candidate if candidate.is_file() else None


def find_validator_python(explicit: str | None) -> str | None:
    candidates = (
        [explicit]
        if explicit
        else [
            sys.executable,
            shutil.which("python3"),
            shutil.which("python"),
            "/usr/bin/python3",
        ]
    )
    tried: set[str] = set()
    for candidate in candidates:
        if not candidate or candidate in tried:
            continue
        tried.add(candidate)
        try:
            probe = subprocess.run(
                [candidate, "-c", "import yaml"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if probe.returncode == 0:
            return candidate
    return None


def run_skill_validator(
    require_validator: bool,
    validator_path: str | None,
    validator_python: str | None,
    errors: list[str],
) -> bool:
    validator = find_skill_validator(validator_path)
    if validator is None:
        message = "skill-creator quick_validate.py was not found"
        if require_validator:
            fail(message, errors)
        else:
            print(f"SKIP {message}")
        return False

    python_executable = find_validator_python(validator_python)
    if python_executable is None:
        requested = validator_python or "the current Python, python3/python on PATH, and /usr/bin/python3"
        message = f"no validator Python with PyYAML was available; tried {requested}"
        if require_validator:
            fail(message, errors)
        else:
            print(f"SKIP {message}; built-in structural checks still ran")
        return False

    if python_executable != sys.executable:
        print(f"INFO quick_validate uses {python_executable}")

    for name in SKILL_NAMES:
        skill_dir = REPO_ROOT / "skills" / name
        try:
            result = subprocess.run(
                [python_executable, str(validator), str(skill_dir)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            fail(f"quick_validate could not run for {name}: {exc}", errors)
            continue
        if result.returncode:
            details = (result.stdout + result.stderr).strip()
            fail(f"quick_validate failed for {name}: {details}", errors)
        else:
            print(f"PASS quick_validate {name}")
    return True


def load_manifest(errors: list[str]) -> dict[str, object] | None:
    initial_error_count = len(errors)
    try:
        manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{SOURCE_MANIFEST.relative_to(REPO_ROOT)} is invalid: {exc}", errors)
        return None

    if not isinstance(manifest, dict):
        fail(f"{SOURCE_MANIFEST.relative_to(REPO_ROOT)} must contain a JSON object", errors)
        return None

    upstream = manifest.get("upstream")
    if not isinstance(upstream, dict):
        fail("source manifest must contain an upstream object", errors)
        return None

    upstream_types = {
        "repository": str,
        "ref": str,
        "reviewed_commit": str,
        "skills": dict,
    }
    for key, expected_type in upstream_types.items():
        if not isinstance(upstream.get(key), expected_type):
            fail(f"source manifest upstream.{key} must be {expected_type.__name__}", errors)

    reviewed_commit = upstream.get("reviewed_commit")
    if isinstance(reviewed_commit, str) and not re.fullmatch(r"[0-9a-f]{40}", reviewed_commit):
        fail("source manifest reviewed_commit must be a 40-character SHA", errors)

    skills = upstream.get("skills")
    if not isinstance(skills, dict):
        fail("source manifest upstream.skills must be an object", errors)
        return None

    upstream_skills = set(skills)
    expected_skills = set(SKILL_NAMES)
    if upstream_skills != expected_skills:
        fail(
            "source manifest skill set mismatch: "
            f"expected {sorted(expected_skills)}, got {sorted(upstream_skills)}",
            errors,
        )

    for local_name in SKILL_NAMES:
        source = skills.get(local_name)
        if not isinstance(source, dict):
            fail(f"source manifest entry {local_name} must be an object", errors)
            continue
        if set(source) != {"sha256"}:
            fail(
                f"source manifest {local_name} must contain only sha256",
                errors,
            )
        source_hash = source.get("sha256")
        if not isinstance(source_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", source_hash):
            fail(f"source manifest {local_name}.sha256 is invalid", errors)

    codex = manifest.get("codex")
    if not isinstance(codex, dict):
        fail("source manifest must contain a codex object", errors)
    else:
        if not isinstance(codex.get("manual"), str):
            fail("source manifest codex.manual must be a string", errors)
        capabilities = codex.get("reviewed_capabilities")
        if not isinstance(capabilities, list) or not all(
            isinstance(item, str) for item in capabilities
        ):
            fail("source manifest codex.reviewed_capabilities must be a string list", errors)
        elif not REQUIRED_CODEX_CAPABILITIES.issubset(set(capabilities)):
            missing = sorted(REQUIRED_CODEX_CAPABILITIES - set(capabilities))
            fail(f"source manifest lacks reviewed Codex capabilities: {missing}", errors)
        evidence = codex.get("capability_evidence")
        if not isinstance(evidence, dict):
            fail("source manifest codex.capability_evidence must be an object", errors)
        elif set(evidence) != REQUIRED_CODEX_CAPABILITIES:
            fail(
                "source manifest Codex evidence set mismatch: "
                f"expected {sorted(REQUIRED_CODEX_CAPABILITIES)}, got {sorted(evidence)}",
                errors,
            )
        else:
            for capability, fragments in evidence.items():
                if not isinstance(fragments, list) or not fragments or not all(
                    isinstance(fragment, str) and fragment for fragment in fragments
                ):
                    fail(
                        f"source manifest Codex evidence for {capability} must be a non-empty string list",
                        errors,
                    )

    if len(errors) != initial_error_count:
        return None
    return manifest


def github_archive_url(repository: str, commit: str) -> str:
    parsed = urlparse(repository)
    path = parsed.path.removesuffix(".git").strip("/")
    parts = path.split("/")
    if parsed.scheme != "https" or parsed.netloc != "github.com" or len(parts) != 2:
        raise ValueError("upstream repository must be an https://github.com/<owner>/<repo> URL")
    owner, repo = parts
    return f"https://codeload.github.com/{owner}/{repo}/tar.gz/{commit}"


def read_skill_hashes_from_archive(fileobj) -> set[str]:
    hashes: set[str] = set()
    with tarfile.open(fileobj=fileobj, mode="r|gz") as archive:
        for member in archive:
            if not member.isfile() or "/skills/" not in member.name or not member.name.endswith("/SKILL.md"):
                continue
            extracted = archive.extractfile(member)
            if extracted is not None:
                hashes.add(hashlib.sha256(extracted.read()).hexdigest())
    return hashes


def check_upstream(manifest: dict[str, object], errors: list[str]) -> None:
    upstream = manifest["upstream"]
    try:
        result = subprocess.run(
            ["git", "ls-remote", upstream["repository"], upstream["ref"]],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"could not read upstream ref: {exc}", errors)
        return
    if result.returncode:
        fail(f"could not read upstream ref: {result.stderr.strip()}", errors)
        return

    remote_fields = result.stdout.split()
    if not remote_fields:
        fail("upstream ref resolved without a commit", errors)
        return
    current_commit = remote_fields[0]
    reviewed_commit = upstream["reviewed_commit"]
    if current_commit == reviewed_commit:
        print(f"PASS upstream commit remains {current_commit}")
    else:
        print(
            f"INFO upstream main moved from {reviewed_commit} to {current_commit}; checking target files"
        )

    try:
        archive_url = github_archive_url(upstream["repository"], current_commit)
        with urlopen(archive_url, timeout=30) as response:
            current_hashes = read_skill_hashes_from_archive(response)
    except (OSError, tarfile.TarError, ValueError) as exc:
        fail(f"could not inspect upstream skill archive: {exc}", errors)
        return

    for local_name, source in upstream["skills"].items():
        if source["sha256"] not in current_hashes:
            fail(
                f"upstream source fingerprint changed for {local_name}: {source['sha256']}",
                errors,
            )
        else:
            print(f"PASS upstream source fingerprint unchanged {local_name}")



def validate_codex_manual_text(
    manifest: dict[str, object],
    manual_text: str,
    errors: list[str],
) -> None:
    evidence = manifest["codex"]["capability_evidence"]
    for capability, fragments in evidence.items():
        missing = [fragment for fragment in fragments if fragment not in manual_text]
        if missing:
            fail(
                f"Codex manual evidence changed for {capability}: missing {missing}",
                errors,
            )
        else:
            print(f"PASS Codex manual still documents {capability}")


def check_codex_docs(manifest: dict[str, object], errors: list[str]) -> None:
    manual_url = manifest["codex"]["manual"]
    try:
        with urlopen(manual_url, timeout=30) as response:
            manual_text = response.read().decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"could not fetch current Codex manual: {exc}", errors)
        return
    validate_codex_manual_text(manifest, manual_text, errors)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-upstream",
        action="store_true",
        help="Compare the tracked source workflows with the recorded upstream snapshot.",
    )
    parser.add_argument(
        "--check-codex-docs",
        action="store_true",
        help="Verify that the current Codex manual still contains evidence for every native capability contract.",
    )
    parser.add_argument(
        "--require-validator",
        action="store_true",
        help="Fail if skill-creator quick_validate.py or its dependency is unavailable.",
    )
    parser.add_argument(
        "--validator-python",
        default=os.environ.get("SKILL_VALIDATOR_PYTHON"),
        help="Python interpreter for quick_validate.py; defaults to the current interpreter, python3/python on PATH, then /usr/bin/python3.",
    )
    parser.add_argument(
        "--validator",
        default=os.environ.get("SKILL_VALIDATOR"),
        help="Explicit skill-creator quick_validate.py path; defaults to SKILL_VALIDATOR, then the current Codex system-skill location.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    manifest = load_manifest(errors)
    for name in SKILL_NAMES:
        skill_dir = REPO_ROOT / "skills" / name
        validate_frontmatter(skill_dir, errors)
        validate_runtime_independence(skill_dir, errors)
        validate_standalone_package(skill_dir, errors)
        validate_bundled_scripts(skill_dir, errors)
        validate_state_contract(skill_dir, errors)
        validate_links(skill_dir, errors)
        validate_catalog_files(skill_dir, errors)

    validate_root_catalog(errors)
    validate_tui_group_manifest(errors)

    validator_ran = run_skill_validator(
        args.require_validator,
        args.validator,
        args.validator_python,
        errors,
    )
    if args.check_upstream and manifest is not None:
        check_upstream(manifest, errors)
    if args.check_codex_docs and manifest is not None:
        check_codex_docs(manifest, errors)

    if errors:
        print(f"\n{len(errors)} validation error(s)")
        return 1
    if validator_ran:
        print("\nAll Codex-native workflow skill checks passed, including quick_validate.")
    else:
        print("\nRepository checks passed; quick_validate was skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
