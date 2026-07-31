from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "visual-match" / "scripts" / "score_visual_match.py"
SPEC = importlib.util.spec_from_file_location("visual_match_score", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
scorer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scorer)


def component_scores(**overrides: int) -> dict[str, int]:
    scores = {name: 100 for name in scorer.COMPONENT_WEIGHTS}
    scores.update(overrides)
    return scores


def difference(
    difference_id: str,
    *,
    priority: str,
    category: str,
) -> dict[str, str]:
    return {
        "id": difference_id,
        "priority": priority,
        "category": category,
        "observation": f"Observed {difference_id}",
        "evidence": f"Evidence for {difference_id}",
    }


def suggestion(difference_id: str) -> dict[str, str]:
    return {
        "difference_id": difference_id,
        "change": f"Fix {difference_id}",
        "next_check": f"Recheck {difference_id}",
    }


def target(
    target_id: str,
    *,
    capture_equivalent: bool = True,
    category_match: bool = True,
    components: dict[str, int] | None = None,
    differences: list[dict[str, str]] | None = None,
    suggestions: list[dict[str, str]] | None = None,
    confidence: str = "high",
    candidate_iteration: int = 1,
) -> dict[str, object]:
    return {
        "id": target_id,
        "reference_path": f"reference/{target_id}.png",
        "candidate_path": f"iterations/{candidate_iteration:03d}/{target_id}.png",
        "capture_equivalent": capture_equivalent,
        "category_match": category_match,
        "component_scores": (
            components
            if capture_equivalent
            else None
        ),
        "differences": differences or [],
        "suggestions": suggestions or [],
        "reasoning": f"Compared {target_id}",
        "confidence": confidence,
    }


def payload(iteration: int, *targets: dict[str, object]) -> dict[str, object]:
    return {"iteration": iteration, "targets": list(targets)}


class VisualMatchScoreTest(unittest.TestCase):
    def test_lowest_paired_image_target_controls_the_report(self):
        mobile_differences = [
            difference("D1", priority="minor", category="layout_geometry"),
            difference("D2", priority="minor", category="spacing_shape"),
            difference("D3", priority="minor", category="responsive_states"),
        ]
        report = scorer.calculate_report(
            payload(
                1,
                target("desktop", components=component_scores()),
                target(
                    "mobile",
                    components=component_scores(
                        layout_geometry=95,
                        spacing_shape=95,
                        responsive_states=95,
                    ),
                    differences=mobile_differences,
                    suggestions=[
                        suggestion("D1"),
                        suggestion("D2"),
                        suggestion("D3"),
                    ],
                ),
            ),
            90,
        )

        self.assertEqual(
            [item["score"] for item in report["targets"]],
            [100, 98],
        )
        self.assertEqual(report["score"], 98)
        self.assertEqual(report["visual_similarity_percent"], 98)
        self.assertEqual(report["verdict"], "pass")
        self.assertTrue(report["visual_pass_candidate"])

    def test_major_difference_prevents_pass_above_threshold(self):
        report = scorer.calculate_report(
            payload(
                1,
                target(
                    "dialog",
                    components=component_scores(interaction_states=89),
                    differences=[
                        difference(
                            "D1",
                            priority="major",
                            category="interaction_states",
                        )
                    ],
                    suggestions=[suggestion("D1")],
                ),
            ),
            90,
        )

        self.assertEqual(report["score"], 99)
        self.assertEqual(report["verdict"], "revise")
        self.assertFalse(report["visual_pass_candidate"])

    def test_non_equivalent_capture_has_no_fidelity_score(self):
        report = scorer.calculate_report(
            payload(
                1,
                target(
                    "desktop",
                    capture_equivalent=False,
                    category_match=False,
                    differences=[
                        difference(
                            "D1",
                            priority="blocking",
                            category="layout_geometry",
                        )
                    ],
                    suggestions=[suggestion("D1")],
                ),
            ),
            90,
        )

        self.assertFalse(report["capture_equivalent"])
        self.assertIsNone(report["score"])
        self.assertEqual(report["verdict"], "fail")
        self.assertFalse(report["visual_pass_candidate"])

    def test_component_below_100_requires_visual_difference_evidence(self):
        with self.assertRaisesRegex(
            scorer.ScoreInputError,
            "below 100 lacks a difference",
        ):
            scorer.calculate_report(
                payload(
                    1,
                    target(
                        "desktop",
                        components=component_scores(layout_geometry=95),
                    ),
                ),
                90,
            )

    def test_every_difference_requires_linked_suggestion(self):
        with self.assertRaisesRegex(
            scorer.ScoreInputError,
            "differences lack suggestions",
        ):
            scorer.calculate_report(
                payload(
                    1,
                    target(
                        "desktop",
                        components=component_scores(layout_geometry=80),
                        differences=[
                            difference(
                                "D1",
                                priority="major",
                                category="layout_geometry",
                            )
                        ],
                    ),
                ),
                90,
            )

    def test_priority_and_component_score_must_agree(self):
        with self.assertRaisesRegex(
            scorer.ScoreInputError,
            "with a major difference must score at most 89",
        ):
            scorer.calculate_report(
                payload(
                    1,
                    target(
                        "desktop",
                        components=component_scores(layout_geometry=95),
                        differences=[
                            difference(
                                "D1",
                                priority="major",
                                category="layout_geometry",
                            )
                        ],
                        suggestions=[suggestion("D1")],
                    ),
                ),
                90,
            )

    def test_score_below_90_cannot_be_hidden_as_minor(self):
        with self.assertRaisesRegex(
            scorer.ScoreInputError,
            "below 90 without a blocking or major difference",
        ):
            scorer.calculate_report(
                payload(
                    1,
                    target(
                        "desktop",
                        components=component_scores(layout_geometry=85),
                        differences=[
                            difference(
                                "D1",
                                priority="minor",
                                category="layout_geometry",
                            )
                        ],
                        suggestions=[suggestion("D1")],
                    ),
                ),
                90,
            )

    def test_category_mismatch_requires_material_difference(self):
        with self.assertRaisesRegex(
            scorer.ScoreInputError,
            "category mismatch requires a blocking or major difference",
        ):
            scorer.calculate_report(
                payload(
                    1,
                    target(
                        "desktop",
                        category_match=False,
                        components=component_scores(),
                    ),
                ),
                90,
            )

    def test_previous_report_exposes_stalled_repeated_difference(self):
        first = scorer.calculate_report(
            payload(
                1,
                target(
                    "desktop",
                    components=component_scores(layout_geometry=80),
                    differences=[
                        difference(
                            "D1",
                            priority="major",
                            category="layout_geometry",
                        )
                    ],
                    suggestions=[suggestion("D1")],
                ),
            ),
            90,
        )
        second = scorer.calculate_report(
            payload(
                2,
                target(
                    "desktop",
                    components=component_scores(layout_geometry=80),
                    differences=[
                        difference(
                            "D1",
                            priority="major",
                            category="layout_geometry",
                        )
                    ],
                    suggestions=[suggestion("D1")],
                    candidate_iteration=2,
                ),
            ),
            90,
            first,
        )

        self.assertEqual(second["progress"]["score_delta"], 0)
        self.assertEqual(
            second["progress"]["repeated_material_difference_ids"],
            ["desktop:D1"],
        )
        self.assertTrue(second["progress"]["stalled"])

    def test_previous_report_requires_fresh_candidate_artifact(self):
        first = scorer.calculate_report(
            payload(1, target("desktop", components=component_scores())),
            90,
        )

        with self.assertRaisesRegex(
            scorer.ScoreInputError,
            "must use a fresh candidate artifact path",
        ):
            scorer.calculate_report(
                payload(2, target("desktop", components=component_scores())),
                90,
                first,
            )

    def test_report_contains_visual_verdict_contract(self):
        report = scorer.calculate_report(
            payload(1, target("desktop", components=component_scores())),
            90,
        )

        for field in (
            "score",
            "verdict",
            "category_match",
            "differences",
            "suggestions",
            "reasoning",
        ):
            self.assertIn(field, report)


if __name__ == "__main__":
    unittest.main()
