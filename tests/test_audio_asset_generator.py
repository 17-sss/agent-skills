from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
import wave


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "audio-asset-generator"
GENERATOR_PATH = SKILL_ROOT / "scripts" / "generate_procedural_sfx.py"
SPEC = importlib.util.spec_from_file_location("audio_asset_generator", GENERATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
generator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(generator)


class AudioAssetGeneratorTest(unittest.TestCase):
    def test_generator_uses_only_python_standard_library(self):
        tree = ast.parse(GENERATOR_PATH.read_text(encoding="utf-8"))
        imported_roots = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module.split(".", 1)[0])

        self.assertEqual(
            imported_roots,
            {"__future__", "argparse", "math", "pathlib", "random", "struct", "wave"},
        )

    def test_all_required_presets_write_valid_normalized_mono_pcm_wav(self):
        expected_frames = {
            "ui-click": 3969,
            "success": 14994,
            "error": 12348,
            "pickup": 10584,
            "whoosh": 18522,
            "impact": 13230,
            "portal": 35280,
        }

        self.assertEqual(set(generator.PRESETS), set(expected_frames))
        with tempfile.TemporaryDirectory() as temp_dir:
            for preset, frame_count in expected_frames.items():
                with self.subTest(preset=preset):
                    output = Path(temp_dir) / f"{preset}.wav"
                    generator.write_wav(output, generator.render(preset, seed=17))

                    payload = output.read_bytes()
                    self.assertGreater(len(payload), 44)
                    self.assertEqual(payload[:4], b"RIFF")
                    self.assertEqual(payload[8:12], b"WAVE")
                    with wave.open(str(output), "rb") as wav:
                        self.assertEqual(wav.getnchannels(), 1)
                        self.assertEqual(wav.getsampwidth(), 2)
                        self.assertEqual(wav.getframerate(), 44100)
                        self.assertEqual(wav.getnframes(), frame_count)
                        frames = wav.readframes(wav.getnframes())

                    samples = struct.unpack(f"<{len(frames) // 2}h", frames)
                    peak = max(abs(sample) for sample in samples)
                    self.assertGreater(peak, 0)
                    self.assertLessEqual(peak, 32767)
                    self.assertAlmostEqual(peak / 32767, 0.92, places=3)

    def test_seed_is_deterministic_and_changes_every_preset_variation(self):
        for preset in generator.PRESETS:
            with self.subTest(preset=preset):
                first = generator.render(preset, seed=41)
                repeated = generator.render(preset, seed=41)
                variation = generator.render(preset, seed=42)
                self.assertEqual(first, repeated)
                self.assertNotEqual(first, variation)

    def test_cli_lists_presets_and_generates_a_real_file(self):
        listed = subprocess.run(
            [sys.executable, str(GENERATOR_PATH), "--list-presets"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(tuple(listed.stdout.splitlines()), generator.PRESETS)

        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "nested" / "impact.wav"
            generated = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR_PATH),
                    "--preset",
                    "impact",
                    "--seed",
                    "9",
                    "--output",
                    str(output),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(generated.returncode, 0, generated.stderr)
            self.assertEqual(generated.stdout.strip(), str(output))
            self.assertTrue(output.is_file())
            self.assertGreater(output.stat().st_size, 44)

    def test_cli_refuses_overwrite_without_explicit_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "pickup.wav"
            output.write_bytes(b"preserve-existing-asset")
            command = [
                sys.executable,
                str(GENERATOR_PATH),
                "--preset",
                "pickup",
                "--output",
                str(output),
            ]

            refused = subprocess.run(
                command,
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(refused.returncode, 2)
            self.assertIn("pass --force to replace it", refused.stderr)
            self.assertEqual(output.read_bytes(), b"preserve-existing-asset")

            replaced = subprocess.run(
                [*command, "--force"],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(replaced.returncode, 0, replaced.stderr)
            self.assertEqual(output.read_bytes()[:4], b"RIFF")

    def test_contract_separates_provider_capabilities_and_unverified_output(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        routing = (SKILL_ROOT / "references" / "provider-routing.md").read_text(
            encoding="utf-8"
        )
        delivery = (SKILL_ROOT / "references" / "web-audio-delivery.md").read_text(
            encoding="utf-8"
        )
        interface = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertIn("Treat voice, music, and sound effects as separate capabilities", skill)
        self.assertIn("Treat unknown pricing or credit use as potentially billable", skill)
        self.assertIn("status: not generated", routing)
        self.assertIn("does not establish music or sound-effect generation", routing)
        self.assertIn("prove access, not approval to incur cost", routing)
        self.assertIn("Assume browsers may block audible autoplay", delivery)
        self.assertIn("do not claim a seamless loop from waveform metadata alone", delivery)
        self.assertIn("allow_implicit_invocation: false", interface)


if __name__ == "__main__":
    unittest.main()
