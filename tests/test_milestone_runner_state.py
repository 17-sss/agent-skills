from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "milestone-runner" / "scripts" / "goal_state.py"
SPEC = importlib.util.spec_from_file_location("milestone_runner_state", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
state_helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(state_helper)


def goal(goal_id: str, title: str) -> dict[str, object]:
    return {
        "id": goal_id,
        "title": title,
        "objective": f"Complete {title.lower()}.",
        "acceptance_criteria": [f"{title} is complete."],
        "verification": [f"Verify {title.lower()}."],
    }


def initial_spec() -> dict[str, object]:
    return {
        "objective": "Complete the durable migration safely.",
        "constraints": ["Preserve existing behavior."],
        "verification": ["All migration checks pass."],
        "goals": [goal("G001", "Contract tests"), goal("G002", "Implementation")],
    }


def completion_evidence() -> dict[str, object]:
    return {
        "summary": "The goal is complete.",
        "artifacts": ["tests/result.txt"],
        "checks": [
            {
                "name": "focused check",
                "status": "passed",
                "evidence": "1 check passed",
            }
        ],
        "residual_risks": [],
    }


def blocker_evidence() -> dict[str, object]:
    return {
        "summary": "The external fixture is unavailable.",
        "blocker": "A credential-gated fixture is required.",
        "attempts": ["Checked local fixtures", "Checked recorded fixtures"],
        "needed_action": "Provide the fixture or authorize a replacement.",
    }


def quality_gate() -> dict[str, object]:
    return {
        "status": "passed",
        "implementation_changed": True,
        "requirements": [
            {
                "requirement": "Complete the durable migration safely.",
                "status": "proved",
                "evidence": "The final implementation satisfies the objective.",
            },
            {
                "requirement": "Preserve existing behavior.",
                "status": "proved",
                "evidence": "Regression checks passed.",
            },
            {
                "requirement": "Contract tests is complete.",
                "status": "proved",
                "evidence": "The contract-test checkpoint passed.",
            },
            {
                "requirement": "Implementation is complete.",
                "status": "proved",
                "evidence": "The implementation checkpoint passed.",
            },
        ],
        "verification": [
            {
                "name": "All migration checks pass.",
                "status": "passed",
                "evidence": "All migration checks passed.",
            },
            {
                "name": "Verify contract tests.",
                "status": "passed",
                "evidence": "The contract checks passed.",
            },
            {
                "name": "Verify implementation.",
                "status": "passed",
                "evidence": "The implementation checks passed.",
            },
        ],
        "review": {
            "status": "passed",
            "evidence": "Independent read-only review found no blocker.",
        },
        "residual_risks": [],
    }


class MilestoneRunnerStateTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Path(self.temporary.name)
        self.spec_path = self.write_json("spec.json", initial_spec())

    def tearDown(self):
        self.temporary.cleanup()

    def write_json(self, name: str, value: object) -> Path:
        path = self.repo / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def run_cli(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["AGENT_WORKFLOWS_NOW"] = "2026-07-20T00:00:00Z"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo-root", str(self.repo), *arguments],
            text=True,
            capture_output=True,
            check=False,
            env=environment,
        )
        if check and result.returncode != 0:
            self.fail(f"command failed: {result.stderr}\n{result.stdout}")
        return result

    def payload(self, *arguments: str) -> dict[str, object]:
        return json.loads(self.run_cli(*arguments).stdout)

    def initialize(self) -> dict[str, object]:
        return self.payload("init", "--slug", "migration", "--spec", str(self.spec_path))

    def complete_goal(self, goal_id: str, revision: int) -> int:
        started = self.payload(
            "start",
            "--slug",
            "migration",
            "--expected-revision",
            str(revision),
            "--goal-id",
            goal_id,
        )
        evidence = self.write_json(f"{goal_id}-complete.json", completion_evidence())
        completed = self.payload(
            "checkpoint",
            "--slug",
            "migration",
            "--expected-revision",
            str(started["revision"]),
            "--goal-id",
            goal_id,
            "--status",
            "complete",
            "--evidence-file",
            str(evidence),
        )
        return int(completed["revision"])

    def test_init_uses_only_the_agent_workflows_namespace(self):
        result = self.initialize()
        plan_dir = self.repo / ".agent-workflows" / "goals" / "migration"
        self.assertEqual(result["revision"], 1)
        self.assertTrue((plan_dir / "brief.md").is_file())
        self.assertTrue((plan_dir / "goals.json").is_file())
        self.assertTrue((plan_dir / "ledger.jsonl").is_file())
        self.assertFalse((self.repo / ".omx").exists())
        self.assertIn(".agent-workflows/goals/migration", result["aggregate_goal"])

    def test_sequential_execution_and_revision_guard(self):
        self.initialize()
        wrong = self.run_cli(
            "start",
            "--slug",
            "migration",
            "--expected-revision",
            "1",
            "--goal-id",
            "G002",
            check=False,
        )
        self.assertEqual(wrong.returncode, 2)
        self.assertIn("next eligible goal is G001", wrong.stderr)

        revision = self.complete_goal("G001", 1)
        status = self.payload("status", "--slug", "migration")
        self.assertEqual(status["current_goal"]["id"], "G002")

        stale = self.run_cli(
            "start",
            "--slug",
            "migration",
            "--expected-revision",
            str(revision - 1),
            check=False,
        )
        self.assertEqual(stale.returncode, 2)
        self.assertIn("revision mismatch", stale.stderr)

    def test_blocked_goal_prevents_later_work_until_resume(self):
        self.initialize()
        started = self.payload(
            "start", "--slug", "migration", "--expected-revision", "1"
        )
        evidence = self.write_json("blocked.json", blocker_evidence())
        blocked = self.payload(
            "checkpoint",
            "--slug",
            "migration",
            "--expected-revision",
            str(started["revision"]),
            "--goal-id",
            "G001",
            "--status",
            "blocked",
            "--evidence-file",
            str(evidence),
        )
        later = self.run_cli(
            "start",
            "--slug",
            "migration",
            "--expected-revision",
            str(blocked["revision"]),
            "--goal-id",
            "G002",
            check=False,
        )
        self.assertEqual(later.returncode, 2)
        self.assertIn("next eligible goal is G001", later.stderr)

        resumed = self.payload(
            "resume",
            "--slug",
            "migration",
            "--expected-revision",
            str(blocked["revision"]),
            "--goal-id",
            "G001",
            "--reason",
            "The fixture is now available.",
        )
        self.assertEqual(resumed["current_goal"]["status"], "in_progress")
        self.assertEqual(resumed["current_goal"]["attempts"], 2)

    def test_replacement_preserves_the_superseded_goal(self):
        self.initialize()
        replacement = self.write_json("replacement.json", goal("G003", "Recorded fixture"))
        replaced = self.payload(
            "replace",
            "--slug",
            "migration",
            "--expected-revision",
            "1",
            "--goal-id",
            "G001",
            "--goal-file",
            str(replacement),
            "--reason",
            "The accepted fixture strategy changed.",
        )
        self.assertEqual(replaced["current_goal"]["id"], "G003")
        plan = json.loads(
            (self.repo / ".agent-workflows/goals/migration/goals.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(plan["goals"][0]["status"], "superseded")
        self.assertEqual(plan["goals"][1]["id"], "G003")
        self.payload("validate", "--slug", "migration")

    def test_replacing_future_work_preserves_an_earlier_blocker(self):
        self.initialize()
        started = self.payload(
            "start", "--slug", "migration", "--expected-revision", "1"
        )
        evidence = self.write_json("blocked.json", blocker_evidence())
        blocked = self.payload(
            "checkpoint",
            "--slug",
            "migration",
            "--expected-revision",
            str(started["revision"]),
            "--goal-id",
            "G001",
            "--status",
            "blocked",
            "--evidence-file",
            str(evidence),
        )
        replacement = self.write_json("replacement.json", goal("G003", "Safer rollout"))
        replaced = self.payload(
            "replace",
            "--slug",
            "migration",
            "--expected-revision",
            str(blocked["revision"]),
            "--goal-id",
            "G002",
            "--goal-file",
            str(replacement),
            "--reason",
            "The rollout contract changed without resolving the first blocker.",
        )
        self.assertEqual(replaced["status"], "blocked")
        self.assertEqual(replaced["current_goal"]["id"], "G001")
        self.payload("validate", "--slug", "migration")

    def test_append_records_a_valid_hash_chained_event(self):
        self.initialize()
        appended_goal = self.write_json("appended.json", goal("G003", "Release audit"))
        result = self.payload(
            "append",
            "--slug",
            "migration",
            "--expected-revision",
            "1",
            "--goal-file",
            str(appended_goal),
            "--reason",
            "The accepted release criteria require a final audit.",
        )
        self.assertEqual(result["current_goal"]["id"], "G001")
        validated = self.payload("validate", "--slug", "migration")
        self.assertEqual(validated["ledger_events"], 2)

    def test_pending_transaction_is_rolled_forward_on_resume(self):
        self.initialize()
        plan_dir = self.repo / ".agent-workflows/goals/migration"
        original_plan = (plan_dir / "goals.json").read_text(encoding="utf-8")
        original_ledger = (plan_dir / "ledger.jsonl").read_text(encoding="utf-8")
        started = self.payload(
            "start", "--slug", "migration", "--expected-revision", "1"
        )
        next_plan = json.loads((plan_dir / "goals.json").read_text(encoding="utf-8"))
        next_ledger = [
            json.loads(line)
            for line in (plan_dir / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        (plan_dir / "goals.json").write_text(original_plan, encoding="utf-8")
        (plan_dir / "ledger.jsonl").write_text(original_ledger, encoding="utf-8")
        (plan_dir / ".pending-transaction.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "plan": next_plan,
                    "ledger": next_ledger,
                }
            ),
            encoding="utf-8",
        )

        recovered = self.payload("status", "--slug", "migration")
        self.assertEqual(recovered["revision"], started["revision"])
        self.assertEqual(recovered["current_goal"]["status"], "in_progress")
        self.assertFalse((plan_dir / ".pending-transaction.json").exists())

    def test_stale_pending_transaction_cannot_roll_back_newer_state(self):
        self.initialize()
        plan_dir = self.repo / ".agent-workflows/goals/migration"
        self.payload("start", "--slug", "migration", "--expected-revision", "1")
        stale_transaction = {
            "schema_version": 1,
            "plan": json.loads((plan_dir / "goals.json").read_text(encoding="utf-8")),
            "ledger": [
                json.loads(line)
                for line in (plan_dir / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
            ],
        }
        evidence = self.write_json("G001-complete.json", completion_evidence())
        completed = self.payload(
            "checkpoint",
            "--slug",
            "migration",
            "--expected-revision",
            "2",
            "--goal-id",
            "G001",
            "--status",
            "complete",
            "--evidence-file",
            str(evidence),
        )
        (plan_dir / ".pending-transaction.json").write_text(
            json.dumps(stale_transaction),
            encoding="utf-8",
        )
        rejected = self.run_cli("status", "--slug", "migration", check=False)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("does not extend the current plan", rejected.stderr)
        current_plan = json.loads((plan_dir / "goals.json").read_text(encoding="utf-8"))
        self.assertEqual(current_plan["revision"], completed["revision"])

    def test_plan_slug_must_match_its_descriptor_opened_directory(self):
        self.initialize()
        source = self.repo / ".agent-workflows/goals/migration"
        copied = self.repo / ".agent-workflows/goals/copied-plan"
        shutil.copytree(source, copied)
        rejected = self.run_cli("status", "--slug", "copied-plan", check=False)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("does not match directory copied-plan", rejected.stderr)

    def test_symlinked_state_namespace_is_rejected(self):
        outside = self.repo / "outside-state"
        outside.mkdir()
        (self.repo / ".agent-workflows").symlink_to(outside, target_is_directory=True)
        result = self.run_cli(
            "init", "--slug", "migration", "--spec", str(self.spec_path), check=False
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("cannot securely initialize", result.stderr)
        self.assertEqual(list(outside.iterdir()), [])

    def test_tampered_ledger_is_rejected(self):
        self.initialize()
        ledger = self.repo / ".agent-workflows/goals/migration/ledger.jsonl"
        entry = json.loads(ledger.read_text(encoding="utf-8"))
        entry["details"]["goal_count"] = 99
        ledger.write_text(json.dumps(entry) + "\n", encoding="utf-8")
        result = self.run_cli("validate", "--slug", "migration", check=False)
        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid hash", result.stderr)

    def test_tampered_plan_projection_and_brief_are_rejected(self):
        self.initialize()
        plan_path = self.repo / ".agent-workflows/goals/migration/goals.json"
        original = plan_path.read_text(encoding="utf-8")
        plan = json.loads(original)
        plan["objective"] = "A different objective."
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        changed_plan = self.run_cli("validate", "--slug", "migration", check=False)
        self.assertEqual(changed_plan.returncode, 2)
        self.assertIn("projection hash", changed_plan.stderr)

        plan_path.write_text(original, encoding="utf-8")
        brief = self.repo / ".agent-workflows/goals/migration/brief.md"
        brief.write_text(brief.read_text(encoding="utf-8") + "\nEdited\n", encoding="utf-8")
        changed_brief = self.run_cli("validate", "--slug", "migration", check=False)
        self.assertEqual(changed_brief.returncode, 2)
        self.assertIn("brief.md does not match", changed_brief.stderr)

    def test_finalize_requires_completed_native_goal_and_quality_gate(self):
        self.initialize()
        revision = self.complete_goal("G001", 1)
        revision = self.complete_goal("G002", revision)
        status = self.payload("status", "--slug", "migration")
        self.assertTrue(status["ready_to_finalize"])

        gate_path = self.write_json("quality-gate.json", quality_gate())
        active_snapshot = self.write_json(
            "active-goal.json",
            {"objective": status["aggregate_goal"], "status": "active"},
        )
        rejected = self.run_cli(
            "finalize",
            "--slug",
            "migration",
            "--expected-revision",
            str(revision),
            "--quality-gate-file",
            str(gate_path),
            "--goal-snapshot-file",
            str(active_snapshot),
            check=False,
        )
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("status must be complete", rejected.stderr)

        incomplete_gate = quality_gate()
        incomplete_gate["requirements"] = incomplete_gate["requirements"][:-1]
        incomplete_gate_path = self.write_json("incomplete-gate.json", incomplete_gate)
        rejected_gate = self.run_cli(
            "finalize",
            "--slug",
            "migration",
            "--expected-revision",
            str(revision),
            "--quality-gate-file",
            str(incomplete_gate_path),
            "--goal-snapshot-file",
            str(
                self.write_json(
                    "early-complete-goal.json",
                    {"goal": {"objective": status["aggregate_goal"], "status": "complete"}},
                )
            ),
            check=False,
        )
        self.assertEqual(rejected_gate.returncode, 2)
        self.assertIn("does not prove required requirements", rejected_gate.stderr)

        complete_snapshot = self.write_json(
            "complete-goal.json",
            {"goal": {"objective": status["aggregate_goal"], "status": "complete"}},
        )
        final = self.payload(
            "finalize",
            "--slug",
            "migration",
            "--expected-revision",
            str(revision),
            "--quality-gate-file",
            str(gate_path),
            "--goal-snapshot-file",
            str(complete_snapshot),
        )
        self.assertEqual(final["status"], "complete")
        self.assertFalse(final["ready_to_finalize"])

    def test_goal_snapshot_rejects_ambiguous_nested_goal_objects(self):
        self.initialize()
        revision = self.complete_goal("G001", 1)
        revision = self.complete_goal("G002", revision)
        status = self.payload("status", "--slug", "migration")
        ambiguous = self.write_json(
            "ambiguous-goal.json",
            {
                "objective": status["aggregate_goal"],
                "status": "complete",
                "goal": {"objective": status["aggregate_goal"], "status": "complete"},
            },
        )
        rejected = self.run_cli(
            "finalize",
            "--slug",
            "migration",
            "--expected-revision",
            str(revision),
            "--quality-gate-file",
            str(self.write_json("quality-gate.json", quality_gate())),
            "--goal-snapshot-file",
            str(ambiguous),
            check=False,
        )
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("exactly one explicit goal object", rejected.stderr)

    def test_non_implementation_plan_uses_not_required_review(self):
        self.initialize()
        revision = self.complete_goal("G001", 1)
        revision = self.complete_goal("G002", revision)
        status = self.payload("status", "--slug", "migration")
        gate = quality_gate()
        gate["implementation_changed"] = False
        gate["review"] = {
            "status": "not_required",
            "evidence": "This fixture represents a documentation-only workflow.",
        }
        result = self.payload(
            "finalize",
            "--slug",
            "migration",
            "--expected-revision",
            str(revision),
            "--quality-gate-file",
            str(self.write_json("non-implementation-gate.json", gate)),
            "--goal-snapshot-file",
            str(
                self.write_json(
                    "non-implementation-goal.json",
                    {"objective": status["aggregate_goal"], "status": "complete"},
                )
            ),
        )
        self.assertEqual(result["status"], "complete")

    def test_init_refuses_overwrite_and_path_traversal(self):
        self.initialize()
        duplicate = self.run_cli(
            "init", "--slug", "migration", "--spec", str(self.spec_path), check=False
        )
        self.assertEqual(duplicate.returncode, 2)
        self.assertIn("already exists", duplicate.stderr)

        traversal = self.run_cli(
            "init", "--slug", "../escape", "--spec", str(self.spec_path), check=False
        )
        self.assertEqual(traversal.returncode, 2)
        self.assertIn("lowercase kebab-case", traversal.stderr)
        self.assertFalse((self.repo.parent / "escape").exists())

    def test_atomic_plan_publication_never_replaces_existing_directory(self):
        source = self.repo / "source-plan"
        destination = self.repo / "existing-plan"
        source.mkdir()
        destination.mkdir()
        (source / "source.txt").write_text("source", encoding="utf-8")
        (destination / "existing.txt").write_text("existing", encoding="utf-8")
        directory_fd = os.open(
            self.repo,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
        )
        try:
            with self.assertRaises(state_helper.StateError):
                state_helper.rename_directory_noreplace(
                    directory_fd,
                    source.name,
                    destination.name,
                )
        finally:
            os.close(directory_fd)
        self.assertTrue((source / "source.txt").is_file())
        self.assertEqual(
            (destination / "existing.txt").read_text(encoding="utf-8"),
            "existing",
        )


if __name__ == "__main__":
    unittest.main()
