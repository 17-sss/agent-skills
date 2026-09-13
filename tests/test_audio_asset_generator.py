from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
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
            {
                "__future__",
                "argparse",
                "math",
                "os",
                "pathlib",
                "random",
                "struct",
                "tempfile",
                "wave",
            },
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

    def test_phase_oscillator_integrates_frequency_sweeps(self):
        frequencies = [700 + (1100 * i / 999) for i in range(1000)]
        oscillator = generator.PhaseOscillator()

        for frequency in frequencies:
            oscillator.sample(frequency)

        expected_phase = (
            2.0 * generator.math.pi * sum(frequencies) / generator.SAMPLE_RATE
        ) % (2.0 * generator.math.pi)
        self.assertAlmostEqual(oscillator.phase, expected_phase, places=12)

    def test_success_note_transition_has_no_full_scale_click(self):
        samples = generator.render("success", seed=17)
        midpoint = len(samples) // 2
        transition = samples[midpoint - 128 : midpoint + 128]
        largest_step = max(
            abs(current - previous)
            for previous, current in zip(transition, transition[1:])
        )

        self.assertLess(largest_step, 0.2)

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

    def test_generator_rejects_output_extension_that_mislabels_wav_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_output = Path(temp_dir) / "impact.mp3"
            samples = generator.render("impact", seed=9)

            with self.assertRaisesRegex(ValueError, r"must use a \.wav extension"):
                generator.write_wav(invalid_output, samples)
            self.assertFalse(invalid_output.exists())

            cli_result = subprocess.run(
                [
                    sys.executable,
                    str(GENERATOR_PATH),
                    "--preset",
                    "impact",
                    "--output",
                    str(invalid_output),
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(cli_result.returncode, 2)
            self.assertIn("must use a .wav extension", cli_result.stderr)
            self.assertFalse(invalid_output.exists())

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

    def test_force_replacement_preserves_existing_asset_when_writing_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "impact.wav"
            original = b"preserve-existing-asset"
            output.write_bytes(original)

            with mock.patch.object(
                generator,
                "_write_wav_stream",
                side_effect=RuntimeError("simulated encoder failure"),
            ):
                with self.assertRaisesRegex(RuntimeError, "simulated encoder failure"):
                    generator.write_wav(
                        output,
                        generator.render("impact", seed=9),
                        overwrite=True,
                    )

            self.assertEqual(output.read_bytes(), original)
            self.assertEqual(list(output.parent.glob(f".{output.name}.*.tmp")), [])

    def test_force_replacement_replaces_symlink_without_touching_its_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "original.wav"
            target.write_bytes(b"preserve-symlink-target")
            output = Path(temp_dir) / "replacement.wav"
            output.symlink_to(target)

            generator.write_wav(
                output,
                generator.render("impact", seed=9),
                overwrite=True,
            )

            self.assertFalse(output.is_symlink())
            self.assertEqual(output.read_bytes()[:4], b"RIFF")
            self.assertEqual(target.read_bytes(), b"preserve-symlink-target")

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
        self.assertIn("For ambience, specify:", skill)
        self.assertIn("For voice, specify:", skill)
        self.assertIn("speaker authorization", skill)
        self.assertIn("status: not generated", routing)
        self.assertIn("does not establish music or sound-effect generation", routing)
        self.assertIn("prove access, not approval to incur cost", routing)
        self.assertIn("For OpenAI text-to-speech output", routing)
        self.assertIn("consent recording and matching audio sample", routing)
        self.assertIn("ai_disclosure:", routing)
        self.assertIn("Assume browsers may block audible autoplay", delivery)
        self.assertIn("do not claim a seamless loop from waveform metadata alone", delivery)
        self.assertIn("allow_implicit_invocation: false", interface)


if __name__ == "__main__":
    unittest.main()
