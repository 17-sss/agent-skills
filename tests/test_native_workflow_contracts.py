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
        package_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((SKILLS / "design-loop").rglob("*"))
            if path.is_file()
        )
        self.assertNotIn("https://github.com/17-sss/agent-skills", package_text)

    def test_spec_interview_is_one_question_read_only_and_drift_aware(self):
        text = read("skills/spec-interview/SKILL.md")
        self.assertIn("single highest-leverage unresolved question", text)
        self.assertIn("Do not implement the solution or modify project files", text)
        self.assertIn("capture a content fingerprint", text)
        self.assertIn("tool-enforced `read-only` boundary", text)
        self.assertIn("skip optional delegation", text)
        self.assertIn("file type, executable mode bits, symlink target", text)
        self.assertIn("delegate recursively", text)
        self.assertIn("Wait for the answer", text)
        self.assertIn("native structured-choice input", text)
        self.assertIn("2 or 3 mutually exclusive options", text)
        self.assertIn("`Other/custom` escape hatch", text)
        self.assertIn("Do not force a closed choice", text)
        self.assertIn("numbered plain-text list", text)
        self.assertIn("genuinely open-ended", text)
        self.assertIn("## Offer an optional next workflow", text)
        self.assertIn("current task's available-skill inventory", text)
        self.assertIn("current agent satisfies the runtime requirements", text)
        self.assertIn("Do not inspect the filesystem", text)
        self.assertIn("Do not install a missing skill", text)
        self.assertIn("If the inventory is unavailable", text)
        self.assertIn("runtime compatibility is unclear", text)
        self.assertIn("Omit this section when the user ends early", text)
        self.assertIn("the user explicitly chooses and invokes", text)

    def test_reviewed_plan_enforces_sequential_independent_gates_and_integrity(self):
        skill = read("skills/reviewed-plan/SKILL.md")
        contract = read("skills/reviewed-plan/references/review-contracts.md")
        self.assertLess(skill.index("**Architect**"), skill.index("**Critic**"))
        self.assertIn("fresh native Codex reviewers", skill)
        self.assertIn("Never run Architect and Critic in parallel", skill)
        self.assertIn("read-only prompt is insufficient", skill)
        self.assertIn("delegate recursively", skill)
        self.assertIn("Critic-driven re-review loop to five iterations", skill)
        self.assertIn("before the first Architect `ACCEPT` do not consume", skill)
        self.assertIn("baseline review and does not consume", skill)
        self.assertIn("starts one re-review iteration", skill)
        self.assertIn("Count the iteration as completed only after the subsequent Critic verdict", skill)
        self.assertIn("five completed Critic-driven re-review iterations without `APPROVE`", skill)
        self.assertIn("all currently identifiable blocking findings in one pass", skill)
        self.assertIn("rather than introducing unrelated non-blocking preferences", skill)
        self.assertNotIn("Limit the full review sequence to five cycles", skill)
        self.assertIn("deterministic content fingerprint", contract)
        self.assertIn("file type, executable mode bits, symlink target", contract)
        self.assertIn("discard the affected verdict", contract)
        self.assertIn("## Offer an optional next workflow", skill)
        self.assertIn("current task's available-skill inventory", skill)
        self.assertIn("current agent satisfies the runtime requirements", skill)
        self.assertIn("Do not inspect the filesystem", skill)
        self.assertIn("Do not install a missing skill", skill)
        self.assertIn("If the inventory is unavailable", skill)
        self.assertIn("the handoff is `NOT APPROVED`", skill)
        self.assertIn("the user explicitly chooses and invokes", skill)

    def test_completion_loop_freezes_scope_and_budgets_review(self):
        skill = read("skills/completion-loop/SKILL.md")
        contract = read("skills/completion-loop/references/verification-contract.md")
        for field in (
            "**Objective**",
            "**In scope**",
            "**Non-goals**",
            "**Deployment target**",
            "**Acceptance criteria**",
            "**Required evidence**",
            "**Risk tier**",
            "**Authorized repositories and external systems**",
        ):
            self.assertIn(field, skill)
        self.assertIn("Freeze the contract once implementation begins", skill)
        self.assertIn("Initial full-scope review: at most one", skill)
        self.assertIn("Blocker repair: focused rereview only", skill)
        self.assertEqual(skill.count("Final full verification: at most one"), 1)
        self.assertIn("one additional full-scope review only", skill)
        self.assertIn("An implementation change invalidates only evidence", skill)
        self.assertIn("material expansion", skill.lower())
        self.assertIn("Do not invent requirements", skill)
        self.assertIn("exact `base...HEAD` range", contract)
        self.assertIn("one deterministic packet digest", contract)
        self.assertIn("known existing failures", contract)

    def test_completion_loop_keeps_scope_drift_deferred_and_deduplicates_evidence(self):
        skill = read("skills/completion-loop/SKILL.md")
        contract = read("skills/completion-loop/references/verification-contract.md")
        self.assertIn(
            "A local-only goal treats a Kubernetes-readiness finding as deferred",
            contract,
        )
        self.assertIn(
            "Defer findings outside the frozen contract",
            contract,
        )
        self.assertIn(
            "Do not rerun an unchanged test when the target fingerprint",
            contract,
        )
        self.assertIn(
            "two consecutive review passes introduce a new blocker category",
            contract,
        )
        self.assertIn(
            "Current implementation or repair creates a regression",
            contract,
        )
        self.assertIn(
            "Spend at most one final full verification",
            contract,
        )
        self.assertIn("task-local evidence ledger", skill)
        self.assertIn("does not authorize destructive actions, commits, new threads", skill)
        self.assertIn("Combine consecutive fixes with the same cause", skill)
        self.assertIn("Do not update it after every small repair", skill)
        self.assertIn("Do not narrate every internal review iteration", skill)

    def test_visual_match_preflights_capture_and_cannot_pass_major_drift(self):
        skill = read("skills/visual-match/SKILL.md")
        routing = read("skills/visual-match/references/capability-routing.md")
        rubric = read("skills/visual-match/references/comparison-rubric.md")
        verdict_contract = read(
            "skills/visual-match/references/visual-verdict-contract.md"
        )
        scorer = read("skills/visual-match/scripts/score_visual_match.py")
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
        self.assertIn("visual_similarity_percent", skill)
        self.assertIn("uses the lowest target as both `score`", skill)
        self.assertIn("score >= 90", skill)
        self.assertIn("Python standard library", skill)
        self.assertIn("do not make another UI edit until", skill)
        self.assertIn("latest candidate has a valid native visual verdict", skill)
        self.assertIn("A missing or invalid report prohibits the next UI edit", skill)
        self.assertIn("same material difference survives two consecutive", skill)
        self.assertIn("Diagnose from outside in", skill)
        self.assertIn("one coherent repair batch", skill)
        self.assertIn("scripts/compare_png.py", skill)
        self.assertIn("fresh final paired-image audit", skill)
        self.assertIn("current task's available-skill inventory", routing)
        self.assertIn("dependency-free PNG comparator", routing)
        self.assertIn("default tolerance is `16`", routing)
        self.assertIn("cannot substitute for paired-image review", routing)
        self.assertIn("never sees or judges pixels itself", verdict_contract)
        self.assertIn("Every next UI edit must cite at least one difference ID", verdict_contract)
        self.assertIn("raw pair before reading implementation code", verdict_contract)
        self.assertIn("## Fresh pass audit", verdict_contract)
        self.assertIn("repeated card or row boundaries", verdict_contract)
        self.assertIn("--previous", verdict_contract)
        self.assertIn("`layout_geometry` | 30", rubric)
        self.assertIn("overall score = visual_similarity_percent = minimum target score", rubric)
        self.assertIn("Never average pixel similarity", rubric)
        self.assertIn("undifferentiated flat list", rubric)
        self.assertIn('"visual_pass_candidate"', scorer)
        self.assertIn('"visual_similarity_percent"', scorer)
        self.assertIn('"verdict": verdict', scorer)
        self.assertIn("repeated_material_difference_ids", scorer)
        self.assertNotIn("subprocess", scorer)
        self.assertNotIn("requests", scorer)

        report = read("docs/native-workflow-forward-test-report.md")
        self.assertIn("Status: partial", report)
        self.assertIn("BLOCKED (environment, expected)", report)
        self.assertIn("Status: pending forward test", report)
        self.assertIn("| PENDING |", report)

    def test_review_gate_supports_change_and_file_snapshots_with_two_lanes(self):
        skill = read("skills/review-gate/SKILL.md")
        contract = read("skills/review-gate/references/review-contract.md")
        self.assertIn("**change review** or **file audit**", skill)
        self.assertIn("## Protect sensitive review material", skill)
        self.assertIn("Never place credential values", skill)
        self.assertIn("non-echoing local checks", skill)
        self.assertIn("parent-only fingerprint", skill)
        self.assertIn("never its value or a value-derived hash", skill)
        self.assertIn("keep its digest inside the parent-only fingerprint", skill)
        self.assertIn("identical sanitized packet", skill)
        self.assertIn("restricted to the sanitized packet", skill)
        self.assertIn("Never ask the user to paste a secret", skill)
        self.assertNotIn("Prefer inline bytes", skill)
        self.assertNotIn("complete file bytes", skill)
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
        self.assertIn("never reproduce the value", contract)
        self.assertIn("packet-only isolation", contract)
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
        classification = read("docs/skill-classification.md")
        for readme_path in ("README.md", "README.ko.md"):
            readme = read(readme_path)
            self.assertIn("### Workflow checker modes", readme)
            self.assertIn("--check-upstream", readme)
            self.assertIn("--check-codex-docs", readme)
        self.assertIn("## Suggested cadence", maintenance)
        self.assertIn("### Checker CLI contract", maintenance)
        self.assertIn("goal-state-cli.md", maintenance)
        self.assertIn("score_visual_match.py", maintenance)
        self.assertIn("minimum runtime surface", classification)
        self.assertIn("`.agents/skills/<skill-name>`", classification)
        self.assertIn("`~/.codex/skills/<skill-name>`", classification)
        self.assertIn("`CODEX_SKILL_NAMES`", classification)

    def test_catalog_groups_every_skill_and_provides_copyable_usage(self):
        common = (
            "design-loop",
            "spec-interview",
            "visual-match",
            "handoff-memory",
            "github-pr-review",
            "github-pr-publish",
            "commit-helper",
        )
        codex_native = (
            "reviewed-plan",
            "completion-loop",
            "milestone-runner",
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

    def test_skills_tui_groups_by_runtime_dependency(self):
        manifest = json.loads(read(".claude-plugin/marketplace.json"))
        codex_native = [
            "reviewed-plan",
            "completion-loop",
            "review-gate",
            "milestone-runner",
        ]
        common = {
            "design-loop",
            "spec-interview",
            "visual-match",
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

        for name in codex_group:
            ui = read(f"skills/{name}/agents/openai.yaml")
            self.assertIn('display_name: "Codex · ', ui)
        for name in {"spec-interview", "visual-match"}:
            ui = read(f"skills/{name}/agents/openai.yaml")
            metadata = read(f"skills/{name}/metadata.json")
            self.assertNotIn('display_name: "Codex · ', ui)
            self.assertIn("Cross-agent", metadata)

        for readme_path in ("README.md", "README.ko.md"):
            readme = read(readme_path)
            self.assertIn("`Codex`:", readme)
            self.assertIn("`Other`:", readme)

    def test_all_six_managed_workflows_are_explicit_and_runtime_independent(self):
        banned = (".omx", "tmux", "ask_codex", "ultrawork", "omx state")
        names = (
            "spec-interview",
            "reviewed-plan",
            "completion-loop",
            "visual-match",
            "review-gate",
            "milestone-runner",
        )
        optional_handoffs = {
            "spec-interview": {
                "reviewed-plan",
                "completion-loop",
                "milestone-runner",
            },
            "reviewed-plan": {"completion-loop", "milestone-runner"},
        }
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
                if other_name in optional_handoffs.get(name, set()):
                    self.assertIn(
                        f"`${other_name}`",
                        combined,
                        f"{name} lacks allowed optional handoff {other_name}",
                    )
                elif other_name != name:
                    self.assertNotIn(other_name, combined, f"{name} depends on {other_name}")


if __name__ == "__main__":
    unittest.main()
