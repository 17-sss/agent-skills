from __future__ import annotations

from pathlib import Path
import json
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS = REPO_ROOT / "skills"


def read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


class NativeWorkflowContractTest(unittest.TestCase):
    def test_design_loop_offers_only_an_approved_isolated_renderer_bootstrap(self):
        skill = read("skills/design-loop/SKILL.md")
        routing = read("skills/design-loop/references/surface-capability-guide.md")
        self.assertIn("offer a minimal isolated Chromium bootstrap", skill)
        self.assertIn("explicit user approval", skill)
        self.assertIn("The skill invocation alone is not installation approval", skill)
        self.assertIn("Do not modify the target repository's manifests", skill)
        self.assertIn("PLAYWRIGHT_BROWSERS_PATH", routing)
        self.assertIn("Do not run `install-deps`, `--with-deps`, `sudo`", routing)
        self.assertIn("Remove task-scoped downloads after use", routing)

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
        routing = read("skills/visual-match/references/capability-routing.md")
        rubric = read("skills/visual-match/references/comparison-rubric.md")
        self.assertIn("Before editing, prove that an available capability can render", skill)
        self.assertIn("stop before editing", skill)
        self.assertIn("offer the minimal isolated Chromium bootstrap", skill)
        self.assertIn("invoking this skill is not installation approval", skill)
        self.assertIn("PLAYWRIGHT_BROWSERS_PATH", routing)
        self.assertIn("Do not use `install-deps`, `--with-deps`, `sudo`", routing)
        self.assertIn("Do not modify project manifests, lockfiles, or `node_modules`", routing)
        self.assertIn("An unresolved blocking or major difference", skill)
        self.assertNotIn("blocked with evidence, or explicitly out of scope", rubric)
        self.assertIn("return `BLOCKED` or `INCOMPLETE`", rubric)
        self.assertIn("Do not submit forms", skill)
        self.assertIn("separate explicit, narrowly scoped authorization", skill)

        report = read("docs/native-workflow-forward-test-report.md")
        self.assertIn("Status: partial", report)
        self.assertIn("BLOCKED (environment, expected)", report)
        self.assertIn("Status: pending forward test", report)
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

    def test_milestone_runner_is_standalone_sequential_and_goal_reconciled(self):
        skill = read("skills/milestone-runner/SKILL.md")
        contract = read("skills/milestone-runner/references/state-contract.md")
        cli_reference = read("skills/milestone-runner/references/goal-state-cli.md")
        script = read("skills/milestone-runner/scripts/goal_state.py")
        self.assertIn("Keep this package standalone", skill)
        self.assertIn("Do not invoke or require another skill", skill)
        self.assertIn("Call `get_goal` first", skill)
        self.assertIn("execute one goal at a time", skill.lower())
        self.assertIn("--expected-revision", skill)
        self.assertIn("fresh independent Codex review", skill)
        self.assertIn("Only now call `update_goal`", skill)
        self.assertIn(".agent-workflows/", contract)
        self.assertIn("ledger.jsonl", contract)
        self.assertIn("goal-state-cli.md", skill)
        self.assertIn("--expected-revision", cli_reference)
        self.assertIn("pending transaction", cli_reference)
        self.assertIn("no delete command", cli_reference)
        self.assertIn('STATE_DIRECTORY = ".agent-workflows"', script)
        self.assertNotIn("create_goal", script)
        self.assertNotIn("update_goal", script)

    def test_catalog_documents_checker_modes_and_update_cadence(self):
        maintenance = read("docs/native-workflow-skills-maintenance.md")
        for readme_path in ("README.md", "README.ko.md"):
            readme = read(readme_path)
            self.assertIn("### Workflow checker modes", readme)
            self.assertIn("--check-upstream", readme)
            self.assertIn("--check-codex-docs", readme)
        self.assertIn("## Suggested cadence", maintenance)
        self.assertIn("### Checker CLI contract", maintenance)
        self.assertIn("goal-state-cli.md", maintenance)

    def test_catalog_groups_every_skill_and_provides_copyable_usage(self):
        common = (
            "design-loop",
            "handoff-memory",
            "github-pr-review",
            "github-pr-publish",
            "commit-helper",
        )
        codex_native = (
            "spec-interview",
            "reviewed-plan",
            "completion-loop",
            "milestone-runner",
            "visual-match",
            "review-gate",
        )
        catalogs = (
            ("README.md", "## Shared Skills", "## Codex-native Workflows", "Usage example:"),
            ("README.ko.md", "## 공통 스킬", "## Codex 특화 워크플로", "사용 예시:"),
        )
        for path, common_heading, codex_heading, usage_label in catalogs:
            readme = read(path)
            self.assertLess(readme.index(common_heading), readme.index(codex_heading))
            for name in common + codex_native:
                heading = f"### {name}"
                start = readme.index(heading)
                end = readme.find("\n### ", start + len(heading))
                section = readme[start:] if end == -1 else readme[start:end]
                self.assertIn(usage_label, section, f"{path} {name} lacks a usage label")
                self.assertIn("```text", section, f"{path} {name} lacks a text code block")
                self.assertIn(f"${name}", section, f"{path} {name} example is not explicit")

    def test_readme_defaults_to_english_and_links_the_korean_catalog(self):
        english = read("README.md")
        korean = read("README.ko.md")
        self.assertIn("## Quick Start", english)
        self.assertIn("## Shared Skills", english)
        self.assertIn("[한국어](README.ko.md)", english)
        self.assertIn("## 빠른 시작", korean)
        self.assertIn("## 공통 스킬", korean)
        self.assertIn("[English](README.md)", korean)

    def test_skills_tui_groups_codex_workflows_and_leaves_common_skills_as_other(self):
        manifest = json.loads(read(".claude-plugin/marketplace.json"))
        codex_native = [
            "spec-interview",
            "reviewed-plan",
            "completion-loop",
            "visual-match",
            "review-gate",
            "milestone-runner",
        ]
        common = {
            "design-loop",
            "handoff-memory",
            "github-pr-review",
            "github-pr-publish",
            "commit-helper",
        }

        groups = {plugin["name"]: plugin for plugin in manifest["plugins"]}
        self.assertEqual(set(groups), {"codex", "other"})
        codex_group = {Path(path).name for path in groups["codex"]["skills"]}
        other_group = {Path(path).name for path in groups["other"]["skills"]}
        self.assertEqual(codex_group, set(codex_native))
        self.assertEqual(other_group, common)
        self.assertTrue(codex_group.isdisjoint(other_group))
        for group in groups.values():
            self.assertEqual(group["source"], "./")
            for path in group["skills"]:
                self.assertTrue((REPO_ROOT / path / "SKILL.md").is_file())

        for readme_path in ("README.md", "README.ko.md"):
            readme = read(readme_path)
            self.assertIn("`Codex`:", readme)
            self.assertIn("`Other`:", readme)

    def test_all_six_packages_are_explicit_and_runtime_independent(self):
        banned = (".omx", "tmux", "ask_codex", "ultrawork", "omx state")
        names = (
            "spec-interview",
            "reviewed-plan",
            "completion-loop",
            "visual-match",
            "review-gate",
            "milestone-runner",
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
            for other_name in names:
                if other_name != name:
                    self.assertNotIn(other_name, combined, f"{name} depends on {other_name}")


if __name__ == "__main__":
    unittest.main()
