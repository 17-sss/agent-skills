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


def target(
    target_id: str,
    *,
    capture_equivalent: bool = True,
    components: dict[str, str] | None = None,
    blocking: int = 0,
    major: int = 0,
    minor: int = 0,
    confidence: str = "high",
):
    return {
        "id": target_id,
        "capture_equivalent": capture_equivalent,
        "components": components
        or {name: "match" for name in scorer.COMPONENT_WEIGHTS},
        "blocking_differences": blocking,
        "major_differences": major,
        "minor_differences": minor,
        "confidence": confidence,
    }


class VisualMatchScoreTest(unittest.TestCase):
    def test_lowest_target_score_controls_the_report(self):
        mobile_components = {
            name: "match" for name in scorer.COMPONENT_WEIGHTS
        }
        mobile_components.update(
            {
                "layout_geometry": "minor",
                "spacing_shape": "minor",
                "responsive_states": "minor",
            }
        )
        report = scorer.calculate_report(
            {
                "targets": [
                    target("desktop"),
                    target("mobile", components=mobile_components, minor=3),
                ]
            },
            90,
        )

        self.assertEqual(
            [item["visual_similarity_percent"] for item in report["targets"]],
            [100, 95],
        )
        self.assertEqual(report["visual_similarity_percent"], 95)
        self.assertTrue(report["visual_pass_candidate"])

    def test_major_difference_prevents_pass_above_threshold(self):
        components = {name: "match" for name in scorer.COMPONENT_WEIGHTS}
        components["interaction_states"] = "major"
        report = scorer.calculate_report(
            {"targets": [target("dialog", components=components, major=1)]},
            90,
        )

        self.assertEqual(report["visual_similarity_percent"], 96)
        self.assertFalse(report["visual_pass_candidate"])

    def test_non_equivalent_capture_has_no_score(self):
        report = scorer.calculate_report(
            {"targets": [target("desktop", capture_equivalent=False)]},
            90,
        )

        self.assertFalse(report["capture_equivalent"])
        self.assertIsNone(report["visual_similarity_percent"])
        self.assertFalse(report["visual_pass_candidate"])

    def test_not_applicable_components_are_normalized(self):
        components = {name: "match" for name in scorer.COMPONENT_WEIGHTS}
        components["responsive_states"] = "not_applicable"
        components["interaction_states"] = "not_applicable"
        report = scorer.calculate_report(
            {"targets": [target("static", components=components)]},
            90,
        )

        self.assertEqual(report["targets"][0]["applicable_weight"], 80)
        self.assertEqual(report["visual_similarity_percent"], 100)
        self.assertTrue(report["visual_pass_candidate"])

    def test_difference_counts_must_match_anchored_levels(self):
        components = {name: "match" for name in scorer.COMPONENT_WEIGHTS}
        components["layout_geometry"] = "blocking"

        with self.assertRaisesRegex(scorer.ScoreInputError, "blocking component level"):
            scorer.calculate_report(
                {"targets": [target("broken", components=components)]},
                90,
            )


if __name__ == "__main__":
    unittest.main()
