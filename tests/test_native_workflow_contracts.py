from __future__ import annotations

from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = REPO_ROOT / "skills"


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class NativeWorkflowContractTest(unittest.TestCase):
    def test_spec_interview_is_one_question_read_only_and_drift_aware(self):
        text = read("skills/spec-interview/SKILL.md")
        self.assertIn("single highest-leverage unresolved question", text)
        self.assertIn("Do not implement the solution or modify project files", text)
        self.assertIn("capture a content fingerprint", text)
        self.assertIn("tool-enforced Codex `read-only` sandbox", text)
        self.assertIn("skip optional delegation", text)
        self.assertIn("file type, executable mode bits, symlink target", text)
        self.assertIn("delegate recursively", text)
        self.assertIn("Wait for the answer", text)

    def test_reviewed_plan_enforces_sequential_independent_gates_and_integrity(self):
        skill = read("skills/reviewed-plan/SKILL.md")
        contract = read("skills/reviewed-plan/references/review-contracts.md")
        self.assertLess(skill.index("**Architect**"), skill.index("**Critic**"))
        self.assertIn("fresh native Codex reviewers", skill)
        self.assertIn("Never run Architect and Critic in parallel", skill)
        self.assertIn("read-only prompt is insufficient", skill)
        self.assertIn("delegate recursively", skill)
        self.assertIn("deterministic content fingerprint", contract)
        self.assertIn("file type, executable mode bits, symlink target", contract)
        self.assertIn("discard the affected verdict", contract)

    def test_completion_loop_rechecks_and_rereviews_the_final_candidate(self):
        skill = read("skills/completion-loop/SKILL.md")
        contract = read("skills/completion-loop/references/verification-contract.md")
        self.assertIn("Any implementation-artifact change after review invalidates", skill)
        self.assertIn("fresh independent review of the new candidate state", skill)
        self.assertIn("--sandbox read-only", skill)
        self.assertIn("must not activate another workflow or delegate recursively", skill)
        self.assertIn("file type, executable mode bits, symlink target", skill)
        self.assertIn("tool-enforced Codex `read-only` sandbox", contract)
        self.assertIn("approval never carries forward across code changes", contract)
        self.assertIn("requirement", contract.lower())

    def test_visual_match_preflights_capture_and_cannot_pass_major_drift(self):
        skill = read("skills/visual-match/SKILL.md")
        rubric = read("skills/visual-match/references/comparison-rubric.md")
        self.assertIn("Before editing, prove that an available capability can render", skill)
        self.assertIn("stop before editing", skill)
        self.assertIn("An unresolved blocking or major difference", skill)
        self.assertNotIn("blocked with evidence, or explicitly out of scope", rubric)
        self.assertIn("return `BLOCKED` or `INCOMPLETE`", rubric)
        self.assertIn("Do not submit forms", skill)
        self.assertIn("separate explicit, narrowly scoped authorization", skill)

        report = read("docs/native-workflow-forward-test-report.md")
        self.assertIn("Status: partial", report)
        self.assertIn("BLOCKED (environment, expected)", report)
        self.assertIn("| PENDING |", report)

    def test_review_gate_supports_change_and_file_snapshots_with_two_lanes(self):
        skill = read("skills/review-gate/SKILL.md")
        contract = read("skills/review-gate/references/review-contract.md")
        self.assertIn("**change review** or **file audit**", skill)
        self.assertIn("complete file bytes or explicit binary hashes", skill)
        self.assertIn("**commit**", skill)
        self.assertIn("**base branch or checked-out PR-style target**", skill)
        self.assertIn("two separate task-scoped copies", skill)
        self.assertIn("Each lane verifies its digest", skill)
        self.assertIn("Each lane is terminal", skill)
        self.assertIn("Git is optional", skill)
        self.assertIn("Spawn both native review lanes in parallel", skill)
        self.assertIn("makes no repository or external-system write", skill)
        self.assertIn("file type, executable mode bits, symlink target", skill)
        self.assertIn("same target-specific recipe", skill)
        self.assertIn("for current changes, recompute", skill)
        self.assertIn("for a commit, re-resolve", skill)
        self.assertIn("for a base branch or checked-out PR-style target", skill)
        self.assertIn("for a file audit, recompute", skill)
        self.assertIn("for a file audit", contract)
        self.assertIn("Final verdict precedence", contract)

    def test_all_five_packages_are_explicit_and_runtime_independent(self):
        banned = (".omx", "tmux", "ask_codex", "ultrawork", "omx state")
        names = (
            "spec-interview",
            "reviewed-plan",
            "completion-loop",
            "visual-match",
            "review-gate",
        )
        for name in names:
            package = SKILLS / name
            openai = (package / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.assertIn("allow_implicit_invocation: false", openai)
            surfaces = []
            for path in sorted(package.rglob("*")):
                if not path.is_file():
                    continue
                try:
                    surfaces.append(path.read_text(encoding="utf-8"))
                except UnicodeDecodeError:
                    continue
            combined = "\n".join(surfaces)
            for pattern in banned:
                self.assertNotIn(pattern, combined.lower(), f"{name} contains {pattern}")


if __name__ == "__main__":
    unittest.main()
