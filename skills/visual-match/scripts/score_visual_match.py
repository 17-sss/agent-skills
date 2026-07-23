#!/usr/bin/env python3
"""Calculate an anchored visual-match score from structured comparison evidence."""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
import sys
from typing import Any


COMPONENT_WEIGHTS = {
    "layout_geometry": 30,
    "typography": 15,
    "color_surface": 15,
    "spacing_shape": 10,
    "assets_content": 10,
    "responsive_states": 10,
    "interaction_states": 10,
}
LEVEL_FACTORS = {
    "match": Decimal("1.0"),
    "minor": Decimal("0.9"),
    "major": Decimal("0.6"),
    "severe": Decimal("0.3"),
    "blocking": Decimal("0.0"),
    "not_applicable": None,
}
CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


class ScoreInputError(ValueError):
    """Raised when comparison evidence violates the scoring contract."""


def require_non_negative_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ScoreInputError(f"{field} must be a non-negative integer")
    return value


def decimal_json_value(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def calculate_target(target: Any) -> dict[str, Any]:
    if not isinstance(target, dict):
        raise ScoreInputError("each target must be an object")

    target_id = target.get("id")
    if not isinstance(target_id, str) or not target_id.strip():
        raise ScoreInputError("each target.id must be a non-empty string")

    capture_equivalent = target.get("capture_equivalent")
    if not isinstance(capture_equivalent, bool):
        raise ScoreInputError(f"target {target_id!r} capture_equivalent must be boolean")

    components = target.get("components")
    if not isinstance(components, dict):
        raise ScoreInputError(f"target {target_id!r} components must be an object")
    if set(components) != set(COMPONENT_WEIGHTS):
        missing = sorted(set(COMPONENT_WEIGHTS) - set(components))
        extra = sorted(set(components) - set(COMPONENT_WEIGHTS))
        raise ScoreInputError(
            f"target {target_id!r} component keys mismatch; missing={missing}, extra={extra}"
        )

    component_points: dict[str, int | float | None] = {}
    earned = Decimal("0")
    applicable = 0
    for name, weight in COMPONENT_WEIGHTS.items():
        level = components[name]
        if level not in LEVEL_FACTORS:
            raise ScoreInputError(
                f"target {target_id!r} component {name!r} has unsupported level {level!r}"
            )
        factor = LEVEL_FACTORS[level]
        if factor is None:
            component_points[name] = None
            continue
        points = Decimal(weight) * factor
        component_points[name] = decimal_json_value(points)
        earned += points
        applicable += weight

    if applicable == 0:
        raise ScoreInputError(f"target {target_id!r} has no applicable scoring component")

    blocking = require_non_negative_int(
        target.get("blocking_differences"),
        f"target {target_id!r} blocking_differences",
    )
    major = require_non_negative_int(
        target.get("major_differences"),
        f"target {target_id!r} major_differences",
    )
    minor = require_non_negative_int(
        target.get("minor_differences"),
        f"target {target_id!r} minor_differences",
    )
    levels = set(components.values())
    if ("blocking" in levels) != (blocking > 0):
        raise ScoreInputError(
            f"target {target_id!r} blocking component level and difference count disagree"
        )
    if bool(levels.intersection({"major", "severe"})) != (major > 0):
        raise ScoreInputError(
            f"target {target_id!r} major component level and difference count disagree"
        )
    confidence = target.get("confidence")
    if confidence not in CONFIDENCE_ORDER:
        raise ScoreInputError(
            f"target {target_id!r} confidence must be high, medium, or low"
        )

    visual_score: int | None = None
    if capture_equivalent:
        visual_score = int(
            ((earned / Decimal(applicable)) * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )

    return {
        "id": target_id,
        "capture_equivalent": capture_equivalent,
        "visual_similarity_percent": visual_score,
        "applicable_weight": applicable,
        "component_levels": components,
        "component_points": component_points,
        "blocking_differences": blocking,
        "major_differences": major,
        "minor_differences": minor,
        "confidence": confidence,
    }


def calculate_report(payload: Any, threshold: int) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ScoreInputError("input root must be an object")
    targets = payload.get("targets")
    if not isinstance(targets, list) or not targets:
        raise ScoreInputError("input must contain a non-empty targets array")

    calculated = [calculate_target(target) for target in targets]
    target_ids = [target["id"] for target in calculated]
    if len(target_ids) != len(set(target_ids)):
        raise ScoreInputError("target ids must be unique")

    capture_equivalent = all(target["capture_equivalent"] for target in calculated)
    scores = [target["visual_similarity_percent"] for target in calculated]
    overall_score = min(scores) if capture_equivalent else None
    blocking = sum(target["blocking_differences"] for target in calculated)
    major = sum(target["major_differences"] for target in calculated)
    minor = sum(target["minor_differences"] for target in calculated)
    confidence = min(
        (target["confidence"] for target in calculated),
        key=CONFIDENCE_ORDER.__getitem__,
    )
    pass_candidate = bool(
        capture_equivalent
        and overall_score is not None
        and overall_score >= threshold
        and blocking == 0
        and major == 0
        and confidence == "high"
    )

    return {
        "threshold": threshold,
        "capture_equivalent": capture_equivalent,
        "visual_similarity_percent": overall_score,
        "visual_pass_candidate": pass_candidate,
        "blocking_differences": blocking,
        "major_differences": major,
        "minor_differences": minor,
        "confidence": confidence,
        "targets": calculated,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate an anchored visual similarity score from JSON evidence."
    )
    parser.add_argument("input", help="JSON evidence path, or - to read stdin")
    parser.add_argument(
        "--threshold",
        type=int,
        default=90,
        help="Accepted semantic score threshold from 0 to 100 (default: 90)",
    )
    args = parser.parse_args()
    if not 0 <= args.threshold <= 100:
        parser.error("--threshold must be between 0 and 100")
    return args


def main() -> int:
    args = parse_args()
    try:
        if args.input == "-":
            payload = json.load(sys.stdin)
        else:
            payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = calculate_report(payload, args.threshold)
    except (OSError, json.JSONDecodeError, ScoreInputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
