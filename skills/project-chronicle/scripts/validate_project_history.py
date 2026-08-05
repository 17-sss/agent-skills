#!/usr/bin/env python3
"""Validate a Project Chronicle document set."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote


ANCHOR_RE = re.compile(
    r"<!--\s*project-chronicle:last-recorded-commit:\s*([^\s]+)\s*-->"
)
ENTRY_NAME_RE = re.compile(r"^\d{4}-\d{2}(?:-\d{2})?-[a-z0-9][a-z0-9-]*\.md$")
COMMIT_HASH_RE = re.compile(r"[0-9a-fA-F]{7,64}")
LOG_RECORD_RE = re.compile(r"^## \d{4}-\d{2}-\d{2} [—-] .+", re.MULTILINE)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
ABSOLUTE_PATH_RE = re.compile(r"(?<![\w.])(?:/[A-Za-z0-9_.-]+){2,}|[A-Za-z]:\\(?:[^\s`]+)")
PLACEHOLDER_RE = re.compile(r"\[(?:TODO|TBD):|<(?:fill|replace|project|path|date)[^>]*>", re.IGNORECASE)
SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{30,}\b"),
    "credential assignment": re.compile(
        r"(?i)\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*[^\s<]{8,}"
    ),
}
REQUIRED_HEADINGS = {
    "README.md": (
        "# Project History",
        "## Purpose and Origins",
        "## What Exists",
        "## Historical Eras",
        "## History Coverage",
        "## Current Sources of Truth",
        "## Reading Guide",
        "## Evidence Policy",
    ),
    "TIMELINE.md": ("# Project Timeline",),
    "LOG.md": ("# Project History Log",),
}
ENTRY_HEADINGS = (
    "## Context",
    "## What Changed",
    "## Why",
    "## Alternatives and Trade-offs",
    "## Outcome and Consequences",
    "## Evidence",
    "## Unknowns",
)


@dataclass
class Finding:
    level: str
    path: str
    message: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Project Chronicle document set.")
    parser.add_argument("--project-root", required=True, help="Repository or project root")
    parser.add_argument(
        "--history-path",
        help="Explicit history directory, absolute or relative to project root",
    )
    parser.add_argument("--strict", action="store_true", help="Require the full document contract")
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Output format"
    )
    return parser.parse_args()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def resolve_history_path(root: Path, explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = root / path
        path = path.resolve()
        if not is_within(path, root):
            raise ValueError("history path must stay inside project root")
        return path
    for relative in (Path("docs/project-history"), Path("docs/history")):
        candidate = (root / relative).resolve()
        if is_within(candidate, root) and is_chronicle_directory(candidate):
            return candidate
    default = (root / "docs/project-history").resolve()
    if not is_within(default, root):
        raise ValueError("default history path resolves outside project root")
    return default


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


def resolve_git_commit(root: Path, revision: str) -> tuple[bool | None, str | None]:
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0 or result.stdout.strip() != "true":
        return None, None
    verify = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", f"{revision}^{{commit}}"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if verify.returncode != 0:
        return False, None
    return True, verify.stdout.strip()


def git_commit_is_head_ancestor(root: Path, revision: str) -> bool | None:
    head_exists, _ = resolve_git_commit(root, "HEAD")
    if head_exists is not True:
        return None
    result = subprocess.run(
        ["git", "-C", str(root), "merge-base", "--is-ancestor", revision, "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None


def relative_label(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def add(finding_list: list[Finding], level: str, path: str, message: str) -> None:
    finding_list.append(Finding(level=level, path=path, message=message))


def validate_links(path: Path, text: str, root: Path, findings: list[Finding]) -> None:
    label = relative_label(path, root)
    for raw_target in MARKDOWN_LINK_RE.findall(text):
        target = raw_target.strip().strip("<>")
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0].split("?", 1)[0]
        if not target:
            continue
        decoded = unquote(target)
        candidate = Path(decoded)
        if candidate.is_absolute() or re.match(r"^[A-Za-z]:\\", decoded):
            add(findings, "error", label, f"non-portable absolute link: {raw_target}")
            continue
        resolved = (path.parent / candidate).resolve()
        if not is_within(resolved, root):
            add(findings, "error", label, f"link escapes project root: {raw_target}")
        elif not resolved.exists():
            add(findings, "error", label, f"broken relative link: {raw_target}")


def validate_text(path: Path, text: str, root: Path, strict: bool, findings: list[Finding]) -> None:
    label = relative_label(path, root)
    validate_links(path, text, root, findings)
    text_without_urls = re.sub(r"https?://[^\s)>]+", "", text)
    for match in ABSOLUTE_PATH_RE.finditer(text_without_urls):
        value = match.group(0)
        if value.startswith(("//", "/docs/")):
            continue
        add(findings, "warning", label, f"possible machine-specific absolute path: {value}")
    for secret_name, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            add(findings, "error", label, f"possible {secret_name} material")
    if strict and PLACEHOLDER_RE.search(text):
        add(findings, "error", label, "contains an unresolved template placeholder")


def validate_history(root: Path, history: Path, strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    history_label = relative_label(history, root)
    if not history.is_dir():
        add(findings, "error", history_label, "history directory does not exist")
        return findings

    loaded: dict[str, str] = {}
    for filename, headings in REQUIRED_HEADINGS.items():
        path = history / filename
        label = relative_label(path, root)
        if not path.is_file():
            add(findings, "error", label, "required history document is missing")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        loaded[filename] = text
        validate_text(path, text, root, strict, findings)
        if strict:
            for heading in headings:
                if heading not in text:
                    add(findings, "error", label, f"missing required heading: {heading}")

    log_text = loaded.get("LOG.md")
    if log_text is not None:
        log_label = relative_label(history / "LOG.md", root)
        anchor_match = ANCHOR_RE.search(log_text)
        if not anchor_match:
            add(findings, "error", log_label, "missing last-recorded-commit marker")
        else:
            anchor = anchor_match.group(1)
            if anchor == "none":
                head_exists, _ = resolve_git_commit(root, "HEAD")
                if head_exists is True:
                    add(findings, "warning", log_label, "Git repository uses a 'none' commit anchor")
            elif not COMMIT_HASH_RE.fullmatch(anchor):
                add(findings, "error", log_label, f"invalid commit anchor format: {anchor}")
            else:
                exists, resolved_anchor = resolve_git_commit(root, anchor)
                if exists is False:
                    add(findings, "error", log_label, f"commit anchor does not resolve: {anchor}")
                elif exists is None:
                    if strict and len(anchor) not in {40, 64}:
                        add(
                            findings,
                            "error",
                            log_label,
                            "strict mode requires a full commit anchor",
                        )
                    add(findings, "warning", log_label, "commit anchor cannot be verified outside Git")
                else:
                    if strict and resolved_anchor and len(anchor) != len(resolved_anchor):
                        add(
                            findings,
                            "error",
                            log_label,
                            f"strict mode requires a full {len(resolved_anchor)}-character commit anchor",
                        )
                    ancestor = git_commit_is_head_ancestor(root, resolved_anchor or anchor)
                    if ancestor is False:
                        add(
                            findings,
                            "error" if strict else "warning",
                            log_label,
                            "commit anchor is not an ancestor of HEAD",
                        )
        if strict and not LOG_RECORD_RE.search(log_text):
            add(findings, "error", log_label, "strict mode requires at least one dated log record")

    timeline_text = loaded.get("TIMELINE.md")
    if strict and timeline_text is not None and not re.search(
        r"^## \d{4}-\d{2}", timeline_text, re.MULTILINE
    ):
        add(
            findings,
            "error",
            relative_label(history / "TIMELINE.md", root),
            "strict mode requires at least one dated timeline period",
        )

    entries_dir = history / "entries"
    if entries_dir.exists() and not entries_dir.is_dir():
        add(findings, "error", relative_label(entries_dir, root), "entries path is not a directory")
    elif entries_dir.is_dir():
        for entry in sorted(entries_dir.glob("*.md")):
            label = relative_label(entry, root)
            if not ENTRY_NAME_RE.fullmatch(entry.name):
                add(findings, "error", label, "entry filename must be YYYY-MM[-DD]-<slug>.md")
            text = entry.read_text(encoding="utf-8", errors="replace")
            validate_text(entry, text, root, strict, findings)
            if strict:
                for heading in ENTRY_HEADINGS:
                    if heading not in text:
                        add(findings, "error", label, f"missing required entry heading: {heading}")

    gaps_path = history / "GAPS.md"
    if gaps_path.is_file():
        gaps_text = gaps_path.read_text(encoding="utf-8", errors="replace")
        validate_text(gaps_path, gaps_text, root, strict, findings)
        if strict and "# Project History Gaps" not in gaps_text:
            add(
                findings,
                "error",
                relative_label(gaps_path, root),
                "missing '# Project History Gaps' heading",
            )

    return findings


def main() -> int:
    args = parse_args()
    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: project root is not a directory: {root}", file=sys.stderr)
        return 2
    try:
        history = resolve_history_path(root, args.history_path)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    findings = validate_history(root, history, args.strict)
    errors = [finding for finding in findings if finding.level == "error"]
    warnings = [finding for finding in findings if finding.level == "warning"]
    result = {
        "valid": not errors,
        "project_root": str(root),
        "history_path": relative_label(history, root),
        "strict": args.strict,
        "errors": [asdict(finding) for finding in errors],
        "warnings": [asdict(finding) for finding in warnings],
    }
    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for finding in findings:
            print(f"{finding.level.upper()}: {finding.path}: {finding.message}")
        status = "PASS" if not errors else "FAIL"
        print(
            f"{status}: {result['history_path']} "
            f"({len(errors)} errors, {len(warnings)} warnings, strict={args.strict})"
        )
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
