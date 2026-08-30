#!/usr/bin/env python3
"""Validate the minimum durable game design contract."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


REQUIRED_HEADINGS = (
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


def section_body(text: str, heading: str) -> str | None:
    match = re.search(rf"(?m)^##\s+{re.escape(heading)}\s*$", text)
    if match is None:
        return None
    remainder = text[match.end() :]
    next_heading = re.search(r"(?m)^##\s+", remainder)
    return remainder[: next_heading.start() if next_heading else len(remainder)].strip()


def validate_design(text: str) -> list[str]:
    errors: list[str] = []
    for heading in REQUIRED_HEADINGS:
        body = section_body(text, heading)
        if body is None:
            errors.append(f"missing required section: ## {heading}")
        elif not body:
            errors.append(f"required section is empty: ## {heading}")
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(text):
            errors.append(f"unresolved placeholder matches {pattern.pattern!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("design", type=Path)
    args = parser.parse_args()

    try:
        text = args.design.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read {args.design}: {exc}", file=sys.stderr)
        return 2

    errors = validate_design(text)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"valid design contract: {args.design}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
