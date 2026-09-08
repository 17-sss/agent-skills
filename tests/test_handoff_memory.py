from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "skills" / "handoff-memory" / "scripts" / "validate_handoff.py"
CREATE = REPO_ROOT / "skills" / "handoff-memory" / "scripts" / "create_handoff.py"
STALENESS = REPO_ROOT / "skills" / "handoff-memory" / "scripts" / "check_staleness.py"


class HandoffMemoryValidatorTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_validator(
        self, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--project-root",
                str(self.project),
                *args,
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", "-C", str(self.project), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

    def init_git_project(self, filenames: tuple[str, ...]) -> None:
        self.git("init")
        self.git("config", "user.name", "Handoff Test")
        self.git("config", "user.email", "handoff@example.com")
        for filename in filenames:
            path = self.project / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"tracked: {filename}\n", encoding="utf-8")
        self.git("add", "--all")
        self.git("commit", "-m", "test: add fixture files")
        handoff = self.project / "docs" / "HANDOFF.md"
        handoff.parent.mkdir(parents=True, exist_ok=True)
        handoff.write_text(
            "# HANDOFF\n\n## Metadata\n\n- Last Updated: 2999-01-01T00:00:00+00:00\n",
            encoding="utf-8",
        )

    def run_staleness(self) -> dict[str, object]:
        result = subprocess.run(
            [
                sys.executable,
                str(STALENESS),
                "--project-root",
                str(self.project),
                "--scope",
                "repo",
                "--format",
                "json",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return json.loads(result.stdout)

    def write_handoff_with_line_count(self, target_line_count: int) -> Path:
        handoff = self.project / "docs" / "HANDOFF.md"
        handoff.parent.mkdir(parents=True, exist_ok=True)
        prefix = """# HANDOFF

## Metadata

- Project: fixture

## TL;DR

- Current state is verified.

## Current Objective

- Keep the fixture resumable.

## Current State

- The validator fixture is ready.

## Recent Changes
"""
        suffix = """
## Known Issues / Watch List

- No known issue.

## Quick Reference

- Key files: `docs/HANDOFF.md`

## Validation

- Checks run: handoff validator

## Next Actions

1. Continue the fixture.

## Resume Checklist

- Re-run the validator.

## Resume Prompt

Continue from the current fixture state.
"""
        base_lines = (prefix + suffix).splitlines()
        filler_count = target_line_count - len(base_lines)
        self.assertGreaterEqual(filler_count, 1)
        filler = "\n".join(
            f"- Completed detail {index}." for index in range(filler_count)
        )
        text = prefix + filler + "\n" + suffix
        self.assertEqual(len(text.splitlines()), target_line_count)
        handoff.write_text(text, encoding="utf-8")
        return handoff

    def test_handoff_length_advisory_reports_boundary_and_largest_sections(self):
        self.write_handoff_with_line_count(220)
        at_limit = self.run_validator(
            "--scope", "repo", "--document", "handoff", "--strict", "--format", "json"
        )
        at_limit_payload = json.loads(at_limit.stdout)

        self.assertTrue(at_limit_payload["valid"])
        self.assertEqual(at_limit_payload["warnings"], [])
        self.assertEqual(at_limit_payload["document_metrics"]["line_count"], 220)
        self.assertEqual(
            at_limit_payload["document_metrics"]["recommended_max_lines"], 220
        )

        self.write_handoff_with_line_count(221)
        over_limit = self.run_validator(
            "--scope", "repo", "--document", "handoff", "--strict", "--format", "json"
        )
        over_limit_payload = json.loads(over_limit.stdout)

        self.assertEqual(over_limit.returncode, 0)
        self.assertTrue(over_limit_payload["valid"])
        self.assertIn("HANDOFF is 221 lines", over_limit_payload["warnings"][0])
        self.assertIn("recommended maximum is 220", over_limit_payload["warnings"][0])
        self.assertIn("snapshot or an existing repository history document", over_limit_payload["warnings"][0])
        self.assertEqual(
            over_limit_payload["document_metrics"]["largest_sections"][0]["name"],
            "Recent Changes",
        )

    def test_length_advisory_uses_the_validator_section_syntax(self):
        handoff = self.write_handoff_with_line_count(221)
        handoff.write_text(
            handoff.read_text(encoding="utf-8").replace("\n## ", "\n##\t"),
            encoding="utf-8",
        )

        result = self.run_validator(
            "--scope", "repo", "--document", "handoff", "--strict", "--format", "json"
        )
        payload = json.loads(result.stdout)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["document_metrics"]["line_count"], 221)
        self.assertEqual(
            payload["document_metrics"]["largest_sections"][0]["name"],
            "Recent Changes",
        )
        self.assertNotIn("Largest sections: .", payload["warnings"][0])

    def test_length_advisory_does_not_apply_to_durable_companion_documents(self):
        decisions = self.project / "_memory" / "DECISIONS.md"
        decisions.parent.mkdir(parents=True)
        decisions.write_text(
            "# DECISIONS\n\n## Decision Log\n\n"
            + "\n".join(f"- Decision {index}." for index in range(230))
            + "\n",
            encoding="utf-8",
        )

        result = self.run_validator(
            "--scope", "workspace", "--document", "decisions", "--strict", "--format", "json"
        )
        payload = json.loads(result.stdout)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["warnings"], [])
        self.assertIsNone(payload["document_metrics"]["recommended_max_lines"])
        self.assertEqual(payload["document_metrics"]["largest_sections"], [])

    def test_staleness_detects_deletion_even_without_dirty_file_mtime(self):
        self.init_git_project(("deleted.txt",))
        (self.project / "deleted.txt").unlink()

        payload = self.run_staleness()

        self.assertTrue(payload["stale"])
        self.assertEqual(payload["scope_status"][0]["dirty_paths_count"], 1)
        self.assertIsNone(payload["scope_status"][0]["latest_dirty_epoch"])
        self.assertIn(str(self.project.resolve()), payload["dirty_repositories"])

    def test_staleness_preserves_unusual_names_and_renames(self):
        self.init_git_project(
            (
                "staged-delete.txt",
                "unstaged-delete.txt",
                "한글.txt",
                "rename-source.txt",
            )
        )
        (self.project / "staged-delete.txt").unlink()
        self.git("add", "staged-delete.txt")
        (self.project / "unstaged-delete.txt").unlink()
        (self.project / "한글.txt").write_text("changed\n", encoding="utf-8")
        self.git("mv", "rename-source.txt", "rename-target.txt")
        (self.project / "tab\tname.txt").write_text("tab\n", encoding="utf-8")
        (self.project / "line\nname.txt").write_text("newline\n", encoding="utf-8")

        payload = self.run_staleness()
        status = payload["scope_status"][0]

        self.assertTrue(payload["stale"])
        self.assertEqual(status["dirty_paths_count"], 6)
        self.assertIsNotNone(status["latest_dirty_epoch"])

    def test_invalid_snapshot_options_do_not_create_documents(self):
        cases = (
            ("--document", "decisions", "--snapshot", "--snapshot-kind", "handoff", "--snapshot-reason", "reason"),
            ("--document", "handoff", "--snapshot", "--snapshot-kind", "handoff"),
            ("--document", "handoff", "--snapshot-label", "named"),
        )
        for args in cases:
            with self.subTest(args=args):
                result = subprocess.run(
                    [
                        sys.executable,
                        str(CREATE),
                        "--project-root",
                        str(self.project),
                        "--scope",
                        "workspace",
                        *args,
                    ],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.project / "_memory").exists())


if __name__ == "__main__":
    unittest.main()
