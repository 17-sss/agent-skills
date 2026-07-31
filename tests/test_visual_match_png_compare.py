from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "skills" / "visual-match" / "scripts" / "compare_png.py"
SPEC = importlib.util.spec_from_file_location("visual_match_png_compare", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
comparator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(comparator)


class VisualMatchPngCompareTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def write_image(
        self,
        name: str,
        width: int,
        height: int,
        pixels: list[tuple[int, int, int]],
    ) -> Path:
        path = self.root / name
        comparator.write_rgb_png(path, width, height, pixels)
        return path

    def test_identical_images_are_fully_similar(self):
        pixels = [(12, 34, 56)] * 16
        reference = self.write_image("reference.png", 4, 4, pixels)
        candidate = self.write_image("candidate.png", 4, 4, pixels)

        report = comparator.compare(reference, candidate)

        self.assertEqual(report["method"], "max_rgb_channel_delta")
        self.assertEqual(report["pixel_similarity_percent"], 100.0)
        self.assertEqual(report["changed_pixel_percent"], 0.0)
        self.assertIsNone(report["changed_bounds"])

    def test_tolerance_bounds_hotspots_and_heatmap_are_deterministic(self):
        reference_pixels = [(255, 255, 255)] * 16
        candidate_pixels = list(reference_pixels)
        candidate_pixels[0] = (245, 245, 245)
        candidate_pixels[15] = (0, 0, 0)
        reference = self.write_image("reference.png", 4, 4, reference_pixels)
        candidate = self.write_image("candidate.png", 4, 4, candidate_pixels)
        heatmap = self.root / "heatmap.png"

        report = comparator.compare(
            reference,
            candidate,
            tolerance=16,
            grid_columns=2,
            grid_rows=2,
            heatmap_path=heatmap,
        )

        self.assertEqual(report["pixel_similarity_percent"], 93.75)
        self.assertEqual(report["changed_pixel_percent"], 6.25)
        self.assertEqual(report["severe_pixel_percent"], 6.25)
        self.assertEqual(
            report["changed_bounds"],
            {"x": 3, "y": 3, "width": 1, "height": 1},
        )
        self.assertEqual(
            (report["hotspots"][0]["column"], report["hotspots"][0]["row"]),
            (1, 1),
        )
        self.assertEqual(report["heatmap_path"], str(heatmap))
        self.assertEqual(comparator.read_png(heatmap)[:2], (4, 4))

    def test_dimension_mismatch_is_rejected(self):
        reference = self.write_image(
            "reference.png",
            2,
            2,
            [(255, 255, 255)] * 4,
        )
        candidate = self.write_image(
            "candidate.png",
            3,
            2,
            [(255, 255, 255)] * 6,
        )

        with self.assertRaisesRegex(
            comparator.PngInputError,
            "image dimensions differ",
        ):
            comparator.compare(reference, candidate)

    def test_grid_cannot_exceed_image_dimensions(self):
        pixels = [(255, 255, 255)] * 4
        reference = self.write_image("reference.png", 2, 2, pixels)
        candidate = self.write_image("candidate.png", 2, 2, pixels)

        with self.assertRaisesRegex(
            comparator.PngInputError,
            "grid dimensions cannot exceed",
        ):
            comparator.compare(
                reference,
                candidate,
                grid_columns=3,
                grid_rows=2,
            )


if __name__ == "__main__":
    unittest.main()
