#!/usr/bin/env python3
"""Validate and aggregate native paired-image visual verdict evidence."""

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
PRIORITIES = {"blocking", "major", "minor"}
CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


class ScoreInputError(ValueError):
    """Raised when native visual verdict evidence violates the contract."""


def require_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ScoreInputError(f"{field} must be a non-empty string")
    return value.strip()


def require_positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ScoreInputError(f"{field} must be a positive integer")
    return value


def require_boolean(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ScoreInputError(f"{field} must be boolean")
    return value


def decimal_json_value(value: Decimal) -> int | float:
    if value == value.to_integral_value():
        return int(value)
    return float(value)


def validate_differences(target: dict[str, Any], target_id: str) -> list[dict[str, str]]:
    raw = target.get("differences")
    if not isinstance(raw, list):
        raise ScoreInputError(f"target {target_id!r} differences must be an array")

    differences: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(raw):
        field = f"target {target_id!r} differences[{index}]"
        if not isinstance(item, dict) or set(item) != {
            "id",
            "priority",
            "category",
            "observation",
            "evidence",
        }:
            raise ScoreInputError(
                f"{field} must contain only id, priority, category, observation, and evidence"
            )
        difference_id = require_non_empty_string(item["id"], f"{field}.id")
        if difference_id in seen_ids:
            raise ScoreInputError(
                f"target {target_id!r} difference ids must be unique: {difference_id!r}"
            )
        seen_ids.add(difference_id)

        priority = item["priority"]
        if priority not in PRIORITIES:
            raise ScoreInputError(f"{field}.priority must be blocking, major, or minor")
        category = item["category"]
        if category not in COMPONENT_WEIGHTS:
            raise ScoreInputError(
                f"{field}.category must be one of {sorted(COMPONENT_WEIGHTS)}"
            )
        differences.append(
            {
                "id": difference_id,
                "priority": priority,
                "category": category,
                "observation": require_non_empty_string(
                    item["observation"], f"{field}.observation"
                ),
                "evidence": require_non_empty_string(
                    item["evidence"], f"{field}.evidence"
                ),
            }
        )
    return differences


def validate_suggestions(
    target: dict[str, Any],
    target_id: str,
    differences: list[dict[str, str]],
) -> list[dict[str, str]]:
    raw = target.get("suggestions")
    if not isinstance(raw, list):
        raise ScoreInputError(f"target {target_id!r} suggestions must be an array")

    difference_ids = {item["id"] for item in differences}
    suggestions: list[dict[str, str]] = []
    linked_ids: set[str] = set()
    for index, item in enumerate(raw):
        field = f"target {target_id!r} suggestions[{index}]"
        if not isinstance(item, dict) or set(item) != {
            "difference_id",
            "change",
            "next_check",
        }:
            raise ScoreInputError(
                f"{field} must contain only difference_id, change, and next_check"
            )
        difference_id = require_non_empty_string(
            item["difference_id"], f"{field}.difference_id"
        )
        if difference_id not in difference_ids:
            raise ScoreInputError(
                f"{field}.difference_id references unknown difference {difference_id!r}"
            )
        linked_ids.add(difference_id)
        suggestions.append(
            {
                "difference_id": difference_id,
                "change": require_non_empty_string(item["change"], f"{field}.change"),
                "next_check": require_non_empty_string(
                    item["next_check"], f"{field}.next_check"
                ),
            }
        )

    missing_suggestions = sorted(
        item["id"]
        for item in differences
        if item["id"] not in linked_ids
    )
    if missing_suggestions:
        raise ScoreInputError(
            f"target {target_id!r} differences lack suggestions: "
            f"{missing_suggestions}"
        )
    return suggestions


def validate_component_scores(
    raw: Any,
    target_id: str,
    capture_equivalent: bool,
    differences: list[dict[str, str]],
) -> dict[str, int] | None:
    if not capture_equivalent:
        if raw is not None:
            raise ScoreInputError(
                f"target {target_id!r} component_scores must be null when captures "
                "are not equivalent"
            )
        return None

    if not isinstance(raw, dict) or set(raw) != set(COMPONENT_WEIGHTS):
        missing = sorted(set(COMPONENT_WEIGHTS) - set(raw or {}))
        extra = sorted(set(raw or {}) - set(COMPONENT_WEIGHTS))
        raise ScoreInputError(
            f"target {target_id!r} component score keys mismatch; "
            f"missing={missing}, extra={extra}"
        )

    scores: dict[str, int] = {}
    differences_by_category: dict[str, list[dict[str, str]]] = {
        name: [] for name in COMPONENT_WEIGHTS
    }
    for difference in differences:
        differences_by_category[difference["category"]].append(difference)

    for name in COMPONENT_WEIGHTS:
        value = raw[name]
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
            raise ScoreInputError(
                f"target {target_id!r} component {name!r} must be an integer from 0 to 100"
            )
        category_differences = differences_by_category[name]
        if value < 100 and not category_differences:
            raise ScoreInputError(
                f"target {target_id!r} component {name!r} below 100 lacks a difference"
            )
        if value == 100 and category_differences:
            raise ScoreInputError(
                f"target {target_id!r} component {name!r} has differences but scores 100"
            )
        if any(item["priority"] == "blocking" for item in category_differences) and value > 39:
            raise ScoreInputError(
                f"target {target_id!r} component {name!r} with a blocking difference "
                "must score at most 39"
            )
        if any(item["priority"] == "major" for item in category_differences) and value > 89:
            raise ScoreInputError(
                f"target {target_id!r} component {name!r} with a major difference "
                "must score at most 89"
            )
        if value <= 39 and not any(
            item["priority"] == "blocking" for item in category_differences
        ):
            raise ScoreInputError(
                f"target {target_id!r} component {name!r} scored 39 or below "
                "without a blocking difference"
            )
        if 40 <= value <= 89 and not any(
            item["priority"] in {"blocking", "major"}
            for item in category_differences
        ):
            raise ScoreInputError(
                f"target {target_id!r} component {name!r} scored below 90 "
                "without a blocking or major difference"
            )
        scores[name] = value
    return scores


def calculate_target(target: Any) -> dict[str, Any]:
    if not isinstance(target, dict):
        raise ScoreInputError("each target must be an object")
    expected_fields = {
        "id",
        "reference_path",
        "candidate_path",
        "capture_equivalent",
        "category_match",
        "component_scores",
        "differences",
        "suggestions",
        "reasoning",
        "confidence",
    }
    if set(target) != expected_fields:
        missing = sorted(expected_fields - set(target))
        extra = sorted(set(target) - expected_fields)
        raise ScoreInputError(
            f"target fields mismatch; missing={missing}, extra={extra}"
        )

    target_id = require_non_empty_string(target["id"], "target.id")
    reference_path = require_non_empty_string(
        target["reference_path"], f"target {target_id!r} reference_path"
    )
    candidate_path = require_non_empty_string(
        target["candidate_path"], f"target {target_id!r} candidate_path"
    )
    if reference_path == candidate_path:
        raise ScoreInputError(
            f"target {target_id!r} reference_path and candidate_path must differ"
        )
    capture_equivalent = require_boolean(
        target["capture_equivalent"], f"target {target_id!r} capture_equivalent"
    )
    category_match = require_boolean(
        target["category_match"], f"target {target_id!r} category_match"
    )
    differences = validate_differences(target, target_id)
    if not category_match and not any(
        item["priority"] in {"blocking", "major"} for item in differences
    ):
        raise ScoreInputError(
            f"target {target_id!r} category mismatch requires a blocking or major difference"
        )
    suggestions = validate_suggestions(target, target_id, differences)
    component_scores = validate_component_scores(
        target["component_scores"],
        target_id,
        capture_equivalent,
        differences,
    )
    reasoning = require_non_empty_string(
        target["reasoning"], f"target {target_id!r} reasoning"
    )
    confidence = target["confidence"]
    if confidence not in CONFIDENCE_ORDER:
        raise ScoreInputError(
            f"target {target_id!r} confidence must be high, medium, or low"
        )

    component_points: dict[str, int | float] | None = None
    visual_score: int | None = None
    if component_scores is not None:
        component_points = {}
        earned = Decimal("0")
        total_weight = sum(COMPONENT_WEIGHTS.values())
        for name, weight in COMPONENT_WEIGHTS.items():
            points = Decimal(weight) * Decimal(component_scores[name]) / Decimal("100")
            component_points[name] = decimal_json_value(points)
            earned += points
        visual_score = int(
            ((earned / Decimal(total_weight)) * Decimal("100")).quantize(
                Decimal("1"),
                rounding=ROUND_HALF_UP,
            )
        )

    return {
        "id": target_id,
        "reference_path": reference_path,
        "candidate_path": candidate_path,
        "capture_equivalent": capture_equivalent,
        "category_match": category_match,
        "score": visual_score,
        "component_scores": component_scores,
        "component_points": component_points,
        "differences": differences,
        "suggestions": suggestions,
        "reasoning": reasoning,
        "confidence": confidence,
    }


def material_difference_ids(targets: list[dict[str, Any]]) -> set[str]:
    return {
        f"{target['id']}:{difference['id']}"
        for target in targets
        for difference in target.get("differences", [])
        if difference.get("priority") in {"blocking", "major"}
    }


def calculate_progress(
    current_iteration: int,
    current_score: int | None,
    current_targets: list[dict[str, Any]],
    previous_report: Any,
) -> dict[str, Any] | None:
    if previous_report is None:
        return None
    if not isinstance(previous_report, dict):
        raise ScoreInputError("previous report must be an object")

    previous_iteration = require_positive_int(
        previous_report.get("iteration"), "previous report iteration"
    )
    if previous_iteration >= current_iteration:
        raise ScoreInputError(
            "current iteration must be greater than the previous report iteration"
        )
    previous_score = previous_report.get("score")
    if previous_score is not None and (
        isinstance(previous_score, bool)
        or not isinstance(previous_score, int)
        or not 0 <= previous_score <= 100
    ):
        raise ScoreInputError("previous report score must be null or an integer from 0 to 100")
    previous_targets = previous_report.get("targets")
    if not isinstance(previous_targets, list):
        raise ScoreInputError("previous report targets must be an array")
    previous_by_id = {
        target.get("id"): target
        for target in previous_targets
        if isinstance(target, dict) and isinstance(target.get("id"), str)
    }
    current_by_id = {target["id"]: target for target in current_targets}
    if set(previous_by_id) != set(current_by_id):
        raise ScoreInputError("target ids must remain stable across iterations")
    for target_id, current_target in current_by_id.items():
        previous_target = previous_by_id[target_id]
        if previous_target.get("reference_path") != current_target["reference_path"]:
            raise ScoreInputError(
                f"target {target_id!r} reference path changed across iterations"
            )
        if previous_target.get("candidate_path") == current_target["candidate_path"]:
            raise ScoreInputError(
                f"target {target_id!r} must use a fresh candidate artifact path"
            )

    repeated_ids = sorted(
        material_difference_ids(current_targets)
        & material_difference_ids(previous_targets)
    )
    score_delta = (
        current_score - previous_score
        if current_score is not None and previous_score is not None
        else None
    )
    return {
        "previous_iteration": previous_iteration,
        "score_delta": score_delta,
        "repeated_material_difference_ids": repeated_ids,
        "stalled": bool(
            score_delta is not None and score_delta <= 0 and repeated_ids
        ),
    }


def calculate_report(
    payload: Any,
    threshold: int,
    previous_report: Any = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict) or set(payload) != {"iteration", "targets"}:
        raise ScoreInputError("input root must contain only iteration and targets")
    iteration = require_positive_int(payload["iteration"], "iteration")
    targets = payload["targets"]
    if not isinstance(targets, list) or not targets:
        raise ScoreInputError("input must contain a non-empty targets array")

    calculated = [calculate_target(target) for target in targets]
    target_ids = [target["id"] for target in calculated]
    if len(target_ids) != len(set(target_ids)):
        raise ScoreInputError("target ids must be unique")

    capture_equivalent = all(target["capture_equivalent"] for target in calculated)
    scores = [target["score"] for target in calculated]
    overall_score = min(scores) if capture_equivalent else None
    category_match = all(target["category_match"] for target in calculated)
    blocking = sum(
        difference["priority"] == "blocking"
        for target in calculated
        for difference in target["differences"]
    )
    major = sum(
        difference["priority"] == "major"
        for target in calculated
        for difference in target["differences"]
    )
    minor = sum(
        difference["priority"] == "minor"
        for target in calculated
        for difference in target["differences"]
    )
    confidence = min(
        (target["confidence"] for target in calculated),
        key=CONFIDENCE_ORDER.__getitem__,
    )
    pass_candidate = bool(
        capture_equivalent
        and overall_score is not None
        and overall_score >= threshold
        and category_match
        and blocking == 0
        and major == 0
        and confidence == "high"
    )
    if not capture_equivalent or not category_match or blocking:
        verdict = "fail"
    elif pass_candidate:
        verdict = "pass"
    else:
        verdict = "revise"

    differences = [
        (
            f"[{target['id']}][{difference['priority']}]"
            f"[{difference['category']}][{difference['id']}] "
            f"{difference['observation']} Evidence: {difference['evidence']}"
        )
        for target in calculated
        for difference in target["differences"]
    ]
    suggestions = [
        (
            f"[{target['id']}][{suggestion['difference_id']}] "
            f"{suggestion['change']} Next check: {suggestion['next_check']}"
        )
        for target in calculated
        for suggestion in target["suggestions"]
    ]
    progress = calculate_progress(
        iteration,
        overall_score,
        calculated,
        previous_report,
    )
    return {
        "iteration": iteration,
        "threshold": threshold,
        "score": overall_score,
        "verdict": verdict,
        "category_match": category_match,
        "differences": differences,
        "suggestions": suggestions,
        "reasoning": " ".join(
            f"{target['id']}: {target['reasoning']}" for target in calculated
        ),
        "capture_equivalent": capture_equivalent,
        "visual_similarity_percent": overall_score,
        "visual_pass_candidate": pass_candidate,
        "blocking_differences": blocking,
        "major_differences": major,
        "minor_differences": minor,
        "confidence": confidence,
        "progress": progress,
        "targets": calculated,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and aggregate native paired-image visual verdict evidence."
    )
    parser.add_argument("input", help="JSON evidence path, or - to read stdin")
    parser.add_argument(
        "--threshold",
        type=int,
        default=90,
        help="Accepted visual score threshold from 0 to 100 (default: 90)",
    )
    parser.add_argument(
        "--previous",
        help="Previous validated report used to calculate iteration progress",
    )
    args = parser.parse_args()
    if not 0 <= args.threshold <= 100:
        parser.error("--threshold must be between 0 and 100")
    return args


def read_json(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    try:
        payload = read_json(args.input)
        previous_report = read_json(args.previous) if args.previous else None
        report = calculate_report(payload, args.threshold, previous_report)
    except (OSError, json.JSONDecodeError, ScoreInputError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
