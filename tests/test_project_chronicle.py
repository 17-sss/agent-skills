from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "project-chronicle"
COLLECTOR = SKILL_ROOT / "scripts" / "collect_history_evidence.py"
VALIDATOR = SKILL_ROOT / "scripts" / "validate_project_history.py"


class ProjectChronicleScriptTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project = Path(self.temp_dir.name)
        self.run_command("git", "init", "-q")
        self.run_command("git", "config", "user.name", "Project Chronicle Test")
        self.run_command("git", "config", "user.email", "chronicle@example.com")
        (self.project / "README.md").write_text("# Fixture\n", encoding="utf-8")
        self.run_command("git", "add", "README.md")
        self.run_command("git", "commit", "-qm", "feat: initialize fixture")
        self.first_commit = self.run_command("git", "rev-parse", "HEAD").stdout.strip()
        self.run_command("git", "tag", "v0.1.0")

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_command(
        self, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            list(args),
            cwd=self.project,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=check,
        )

    def run_script(
        self, script: Path, *args: str, check: bool = True
    ) -> subprocess.CompletedProcess[str]:
        return self.run_command(
            sys.executable,
            str(script),
            "--project-root",
            str(self.project),
            *args,
            check=check,
        )

    def write_valid_history(self, anchor: str | None = None) -> Path:
        anchor = anchor or self.first_commit
        history = self.project / "docs" / "project-history"
        entries = history / "entries"
        entries.mkdir(parents=True)
        (history / "README.md").write_text(
            """# Project History

## Purpose and Origins

The fixture verifies the history contract.

## What Exists

One test repository.

## Historical Eras

- `2026-08` — Initial fixture.

## History Coverage

- Earliest verified evidence: initial commit.
- Latest recorded commit: current anchor.

## Current Sources of Truth

- Runtime behavior: `README.md`.

## Reading Guide

- Start with [the timeline](TIMELINE.md).

## Evidence Policy

Facts cite repository evidence; unknowns remain explicit.
""",
            encoding="utf-8",
        )
        (history / "TIMELINE.md").write_text(
            """# Project Timeline

## 2026-08 — Initial fixture

- **Context:** Establish a deterministic test repository.
- **Evolution:** Added the initial project artifact.
- **Outcome:** The chronicle scripts can be tested.
- **Evidence:** [Detailed entry](entries/2026-08-initial-fixture.md).
""",
            encoding="utf-8",
        )
        (history / "LOG.md").write_text(
            f"""# Project History Log

<!-- project-chronicle:last-recorded-commit: {anchor} -->

## 2026-08-03 — Initial history bootstrap

- Type: bootstrap
- Period: 2026-08
- Summary: Recorded the fixture origin.
- Evidence: `{anchor}`
- Detailed entry: [Initial fixture](entries/2026-08-initial-fixture.md)
- Uncommitted evidence: history documents
""",
            encoding="utf-8",
        )
        (entries / "2026-08-initial-fixture.md").write_text(
            f"""# Initial fixture

- Period: 2026-08
- Type: milestone
- Evidence status: verified
- Anchors: `{anchor}`

## Context

The script needed an isolated repository.

## What Changed

The initial fixture was committed.

## Why

It provides deterministic evidence.

## Alternatives and Trade-offs

No material alternative was recorded.

## Outcome and Consequences

Collector and validator behavior can be verified.

## Evidence

- Commits: `{anchor}`

## Unknowns

- None known.
""",
            encoding="utf-8",
        )
        return history

    def test_collector_bootstraps_git_and_document_evidence(self):
        result = self.run_script(COLLECTOR, "--since", "auto", "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(payload["history"]["path"], "docs/project-history")
        self.assertEqual(payload["history"]["selection"], "default")
        self.assertIn("README.md", payload["documents"]["paths"])
        self.assertEqual(payload["git"]["base_anchor"], None)
        self.assertEqual([item["hash"] for item in payload["git"]["commits"]], [self.first_commit])
        self.assertEqual(payload["git"]["tags"][0]["name"], "v0.1.0")
        self.assertFalse(payload["git"]["commits_truncated"])

    def test_collector_does_not_reuse_an_unrelated_docs_history_directory(self):
        unrelated = self.project / "docs" / "history"
        unrelated.mkdir(parents=True)
        (unrelated / "legacy-note.md").write_text("# Legacy note\n", encoding="utf-8")

        result = self.run_script(COLLECTOR, "--since", "auto", "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(payload["history"]["path"], "docs/project-history")
        self.assertEqual(payload["history"]["selection"], "default")

    def test_collector_handles_an_unborn_git_repository(self):
        with tempfile.TemporaryDirectory() as empty_dir:
            empty_project = Path(empty_dir)
            subprocess.run(
                ["git", "init", "-q"],
                cwd=empty_project,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(COLLECTOR),
                    "--project-root",
                    str(empty_project),
                    "--since",
                    "auto",
                    "--format",
                    "json",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        payload = json.loads(result.stdout)

        self.assertTrue(payload["git"]["available"])
        self.assertIsNone(payload["git"]["head"])
        self.assertEqual(payload["git"]["revision_range"], "unborn HEAD")
        self.assertEqual(payload["git"]["commits"], [])

    def test_collector_keeps_document_evidence_without_git(self):
        with tempfile.TemporaryDirectory() as plain_dir:
            plain_project = Path(plain_dir)
            (plain_project / "README.md").write_text("# Plain project\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(COLLECTOR),
                    "--project-root",
                    str(plain_project),
                    "--format",
                    "json",
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        payload = json.loads(result.stdout)

        self.assertFalse(payload["git"]["available"])
        self.assertIn("README.md", payload["documents"]["paths"])

    def test_collector_uses_log_anchor_for_incremental_range(self):
        self.write_valid_history()
        (self.project / "feature.txt").write_text("next milestone\n", encoding="utf-8")
        self.run_command("git", "add", "feature.txt")
        self.run_command("git", "commit", "-qm", "feat: add next milestone")
        second_commit = self.run_command("git", "rev-parse", "HEAD").stdout.strip()

        result = self.run_script(COLLECTOR, "--since", "auto", "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(payload["git"]["base_anchor"], self.first_commit)
        self.assertTrue(payload["git"]["anchor_is_ancestor"])
        self.assertEqual([item["hash"] for item in payload["git"]["commits"]], [second_commit])
        self.assertEqual(payload["git"]["commits"][0]["paths"], ["feature.txt"])
        self.assertTrue(payload["git"]["dirty"])

    def test_strict_validator_accepts_complete_history(self):
        self.write_valid_history()
        result = self.run_script(VALIDATOR, "--strict", "--format", "json")
        payload = json.loads(result.stdout)

        self.assertTrue(payload["valid"])
        self.assertEqual(payload["errors"], [])

    def test_validator_rejects_broken_relative_link(self):
        history = self.write_valid_history()
        readme = history / "README.md"
        readme.write_text(
            readme.read_text(encoding="utf-8") + "\n[Missing evidence](missing.md)\n",
            encoding="utf-8",
        )

        result = self.run_script(VALIDATOR, "--strict", "--format", "json", check=False)
        payload = json.loads(result.stdout)

        self.assertEqual(result.returncode, 1)
        self.assertFalse(payload["valid"])
        self.assertTrue(any("broken relative link" in item["message"] for item in payload["errors"]))


class ProjectChronicleContractTest(unittest.TestCase):
    def test_skill_keeps_log_timeline_and_handoff_boundaries_explicit(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        recording = (SKILL_ROOT / "references" / "recording-rules.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("Every Bootstrap or Record run must add one dated `LOG.md` record", skill)
        self.assertIn("Keep history distinct from handoff state", skill)
        self.assertIn("Update the current period", recording)
        self.assertNotIn("create_goal", skill)
        self.assertNotIn("update_goal", skill)
        self.assertTrue(os.access(COLLECTOR, os.X_OK))
        self.assertTrue(os.access(VALIDATOR, os.X_OK))


if __name__ == "__main__":
    unittest.main()
