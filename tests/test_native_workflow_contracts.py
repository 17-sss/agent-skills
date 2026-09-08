from __future__ import annotations

from pathlib import Path
import ast
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

    def test_design_loop_product_design_routing_is_optional_and_standalone(self):
        skill = read("skills/design-loop/SKILL.md")
        routing = read("skills/design-loop/references/surface-capability-guide.md")
        self.assertIn("Product Design is explicitly invoked", skill)
        self.assertIn("Keep the package usable when that plugin is unavailable", skill)
        self.assertIn("## Optional Product Design Routing", routing)
        self.assertIn("optional accelerators, not package dependencies", routing)
        self.assertIn("current task's available-skill inventory", routing)
        self.assertIn("Do not inspect the filesystem", routing)
        self.assertIn("do not install a missing plugin or skill", routing)
        self.assertIn("`$product-design:ideate`", routing)
        self.assertIn("`$product-design:audit`", routing)
        self.assertIn("`$product-design:image-to-code`", routing)
        self.assertIn("`$product-design:url-to-code`", routing)
        self.assertIn("Return to this rendered evidence loop", routing)
        self.assertIn("does not waive local repository constraints", routing)

    def test_github_pr_review_discloses_posting_details_only_after_authorization(self):
        skill = read("skills/github-pr-review/SKILL.md")
        posting = read("skills/github-pr-review/references/posting-reviews.md")
        self.assertIn("### 7. Publish Only After Authorization", skill)
        self.assertIn("Stop after the draft", skill)
        self.assertIn("read [posting-reviews.md]", skill)
        self.assertNotIn('"comments": [', skill)
        self.assertIn("Read this reference only after", posting)
        self.assertIn("gh pr review <pr> --comment", posting)
        self.assertIn("use `side: RIGHT`", posting)
        self.assertIn('"comments": [', posting)
        self.assertIn("--input /tmp/owner-repo-pr123-review.json", posting)
        self.assertIn('Only set `"event": "APPROVE"`', posting)
        self.assertIn("`user.login` matches the authenticated account", posting)
        self.assertIn("Delete the exact task-scoped payload", posting)

    def test_handoff_memory_routes_detail_without_losing_resume_contract(self):
        skill = read("skills/handoff-memory/SKILL.md")
        usage = read("skills/handoff-memory/references/agent-usage-best-practices.md")
        workspace = read("skills/handoff-memory/references/workspace-memory-guide.md")
        snapshots = read("skills/handoff-memory/references/snapshot-strategy.md")
        self.assertIn("## Core Contract", skill)
        self.assertIn("ambiguous result instead of guessing", skill)
        self.assertIn("`Next Actions` as the default execution queue", skill)
        self.assertIn("--resume --format json", skill)
        self.assertIn("--workspace-wide", skill)
        self.assertIn("## Reference Routing", skill)
        self.assertIn("Resume Execution Priority", usage)
        self.assertIn("`last_active_workstream`", workspace)
        self.assertIn("## When Not to Create a Snapshot", snapshots)

    def test_handoff_memory_offers_chronicle_only_as_a_standalone_follow_up(self):
        skill = read("skills/handoff-memory/SKILL.md")
        usage = read("skills/handoff-memory/references/agent-usage-best-practices.md")
        metadata = read("skills/handoff-memory/metadata.json")
        scripts = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((SKILLS / "handoff-memory" / "scripts").glob("*.py"))
        )

        self.assertIn("## Offer an Optional Durable-History Follow-Up", skill)
        self.assertIn("Keep this package complete on its own", skill)
        self.assertIn("current task's available-skill inventory", skill)
        self.assertIn("Do not inspect installation directories", skill)
        self.assertIn("do not install a missing skill", skill)
        self.assertIn("Offer at most one recommendation", skill)
        self.assertIn("the user explicitly chooses and invokes", skill)
        self.assertIn("`$project-chronicle`", skill)
        self.assertIn("Complete the HANDOFF compaction first", usage)
        self.assertNotIn("project-chronicle", scripts)
        self.assertNotIn("project-chronicle", json.loads(metadata)["references"])

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
        self.assertIn("Pre-acceptance Architect review is still progress-bounded", skill)
        self.assertIn("supplies no new repository evidence", skill)
        self.assertIn("requires an external decision or evidence that is unavailable", skill)
        self.assertIn("baseline review and does not consume", skill)
        self.assertIn("starts one re-review iteration", skill)
        self.assertIn("Count the iteration as completed only after the subsequent Critic verdict", skill)
        self.assertIn("five completed Critic-driven re-review iterations without `APPROVE`", skill)
        self.assertIn("all currently identifiable blocking findings in one pass", skill)
        self.assertIn("rather than introducing unrelated non-blocking preferences", skill)
        self.assertIn("Repeating a previously addressed finding without new evidence", contract)
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

    def test_completion_loop_requires_execution_authority_and_reuses_plans(self):
        skill = read("skills/completion-loop/SKILL.md")
        interface = read("skills/completion-loop/agents/openai.yaml")
        self.assertIn("Approval to write a plan is not approval to execute it", skill)
        self.assertIn("instead of replanning from scratch", skill)
        self.assertIn("small fix needs no separate planning ceremony", skill)
        self.assertIn("does not authorize goal creation, a mode switch, commits, or remote work", skill)
        self.assertIn("do not request it again", skill)
        self.assertIn("allow_implicit_invocation: false", interface)
        self.assertIn("implement the approved plan", interface)

    def test_completion_loop_invalidation_preserves_required_gates(self):
        skill = read("skills/completion-loop/SKILL.md")
        contract = read("skills/completion-loop/references/verification-contract.md")
        for identity in ("dirty diff fingerprint", "shared dependency/lockfile", "fixture/seed", "build identity", "host/environment", "baseline branch identity"):
            self.assertIn(identity, contract)
        self.assertIn("do not count one cached result as multiple passes", contract)
        self.assertIn("Impact cannot safely be narrowed | Rerun the whole required suite", contract)
        self.assertIn("it is never evidence of completion", contract)
        self.assertIn("Do not infer tokens from build duration or CPU load", contract)
        self.assertIn("tool-enforced read-only execution", skill)
        self.assertIn("Keep it terminal and prevent recursive delegation", skill)
        self.assertIn("independent correctness plus architecture review", contract)
        self.assertIn("remains missing evidence, never a pass", contract)
        self.assertIn("only when the approved contract defines that split", contract)

    def test_completion_loop_browser_contract_protects_observations_and_resources(self):
        skill = read("skills/completion-loop/SKILL.md")
        browser = read("skills/completion-loop/references/browser-verification.md")
        self.assertIn("[browser-verification.md](references/browser-verification.md) only when", skill)
        for guard in (
            "Reuse the repository's runner",
            "Do not automatically multiply",
            "three actual reviews",
            "Do not rebuild static output while",
            "A listening port alone does not prove readiness",
            "Readiness waits must not weaken product timing requirements",
            "A browser `404` alone does not identify the class",
            "Change an expectation only with independent evidence",
            "owned processes and descendants exited",
            "never kill shared or user-owned sessions",
        ):
            self.assertIn(guard, browser)

    def test_completion_loop_handoff_timing_never_implies_authority(self):
        skill = read("skills/completion-loop/SKILL.md")
        contract = read("skills/completion-loop/references/verification-contract.md")
        maintenance = read("docs/native-workflow-skills-maintenance.md")
        self.assertIn("Update HANDOFF or project history only when separately requested by the user", skill)
        self.assertIn("Only after a separate user request, refresh HANDOFF or project history", contract)
        self.assertIn("HANDOFF and project-history updates require a separate user request", maintenance)
        self.assertNotIn("Refresh a handoff only at a stable checkpoint", skill + contract)
        for state in ("implementation complete", "integration verification in progress", "awaiting real-device verification"):
            self.assertIn(state, skill)
            self.assertIn(state, contract)

    def test_completion_loop_eval_corpus_covers_entry_and_failure_boundaries(self):
        # Corpus integrity only; behavior is judged from independent forward traces.
        cases = json.loads(read("skills/completion-loop/evals/validation_queries.json"))
        by_id = {case["id"]: case for case in cases}
        self.assertEqual(len(by_id), len(cases))
        self.assertEqual(
            {case["id"] for case in cases if not case["should_trigger"]},
            {"plan-only", "brainstorm", "research", "usage-question"},
        )
        self.assertEqual(
            {case["id"] for case in cases if case["should_trigger"]},
            {"approved-plan", "small-bug-fix", "docs-only", "shared-dependency", "browser-404", "three-visual-reviews", "required-device-missing", "handoff-unapproved", "handoff-push-not-authorized"},
        )
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertIs(type(case["should_trigger"]), bool)
                for field in ("query", "context", "expected_behavior"):
                    self.assertIsInstance(case[field], str)
                    self.assertTrue(case[field].strip())
        example = "/goal Implement the approved plan within its scope and completion criteria. Use $completion-loop."
        for catalog in ("README.md", "README.ko.md"):
            self.assertIn(example, read(catalog))

    def test_pending_forward_eval_corpora_keep_inputs_blind_and_boundaries_explicit(self):
        expected_ids = {
            "spec-interview": {
                "bounded-native-choice",
                "bounded-numbered-fallback",
                "open-ended-free-form",
                "no-automatic-follow-up",
            },
            "visual-match": {
                "renderer-missing-approval-required",
                "renderer-missing-install-declined",
            },
        }
        for name, ids in expected_ids.items():
            cases = json.loads(read(f"skills/{name}/evals/validation_queries.json"))
            self.assertEqual({case["id"] for case in cases}, ids)
            for case in cases:
                with self.subTest(skill=name, case=case["id"]):
                    self.assertEqual(
                        set(case),
                        {"id", "query", "context", "should_trigger", "expected_behavior"},
                    )
                    self.assertIs(type(case["should_trigger"]), bool)
                    for field in ("id", "query", "context", "expected_behavior"):
                        self.assertIsInstance(case[field], str)
                        self.assertTrue(case[field].strip())

        maintenance = read("docs/native-workflow-skills-maintenance.md")
        report = read("docs/native-workflow-forward-test-report.md")
        self.assertIn("Spec Interview](../skills/spec-interview/evals/validation_queries.json)", maintenance)
        self.assertIn("Visual Match](../skills/visual-match/evals/validation_queries.json)", maintenance)
        self.assertIn("authentication failure before workflow selection", report)
        self.assertIn("cross-agent Low-risk execution remains pending", report)

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
        openai = read("skills/review-gate/agents/openai.yaml")
        metadata = read("skills/review-gate/metadata.json")
        self.assertIn("pre-PR or pre-merge gate", skill)
        self.assertIn("native `/review` for a routine or lightweight", skill)
        self.assertIn("Strict pre-PR and pre-merge review gate", openai)
        self.assertIn("routine review to native review tooling", metadata)
        self.assertIn("native `/review`", read("README.md"))
        self.assertIn("native `/review`", read("README.ko.md"))
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

    def test_checker_common_inventory_covers_every_installable_skill(self):
        checker_text = read("scripts/check-native-workflow-skills.py")
        checker_tree = ast.parse(checker_text)
        installable = None
        for node in checker_tree.body:
            if (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "INSTALLABLE_SKILL_NAMES"
            ):
                installable = ast.literal_eval(node.value)
                break

        discovered = tuple(
            sorted(path.parent.name for path in SKILLS.glob("*/SKILL.md"))
        )
        self.assertEqual(tuple(sorted(installable or ())), discovered)
        self.assertIn("for name in INSTALLABLE_SKILL_NAMES:", checker_text)
        self.assertIn("for name in NATIVE_WORKFLOW_SKILL_NAMES:", checker_text)
        self.assertIn("tuple(lines[4:]) not in ((), optional_policy)", checker_text)
        self.assertIn("Empty metadata reference lists are valid", read("docs/native-workflow-skills-maintenance.md"))

        for name in discovered:
            metadata = json.loads(read(f"skills/{name}/metadata.json"))
            for reference in metadata["references"]:
                self.assertTrue(reference.startswith("https://"), (name, reference))
        self.assertEqual(json.loads(read("skills/handoff-memory/metadata.json"))["references"], [])
        self.assertEqual(json.loads(read("skills/project-chronicle/metadata.json"))["references"], [])

    def test_agent_adapter_examples_follow_current_capability_boundaries(self):
        handoff_skill = read("skills/handoff-memory/SKILL.md")
        handoff_readme = read("skills/handoff-memory/README.md")
        handoff_adapters = read("skills/handoff-memory/references/agent-integrations.md")
        review_skill = read("skills/github-pr-review/SKILL.md")
        review_readme = read("skills/github-pr-review/README.md")
        review_adapters = read("skills/github-pr-review/references/agent-adapters.md")

        self.assertIn("global and neutral project-local install locations", handoff_skill)
        for text in (handoff_readme, handoff_adapters):
            self.assertIn("<repo>/.agents/skills/handoff-memory", text)
            self.assertNotIn("<repo>/.codex/skills/handoff-memory", text)
        self.assertIn("capability-conditional network notes", review_skill)
        self.assertIn("Capability-conditional", review_readme)
        self.assertIn("active shell tool schema exposes it", review_adapters)
        self.assertIn("current approval policy permits it", review_adapters)
        self.assertIn("do not pass an unsupported argument", review_adapters)

    def test_catalog_groups_every_skill_and_provides_copyable_usage(self):
        common = (
            "design-loop",
            "godot-dev-loop",
            "spec-interview",
            "completion-loop",
            "visual-match",
            "handoff-memory",
            "project-chronicle",
            "github-pr-review",
            "github-pr-publish",
            "commit-helper",
        )
        codex_native = (
            "reviewed-plan",
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

    def test_skills_tui_groups_by_purpose_and_status_preserve_runtime_dependency(self):
        manifest = json.loads(read(".claude-plugin/marketplace.json"))
        codex_native = [
            "reviewed-plan",
            "review-gate",
            "milestone-runner",
        ]
        common = {
            "design-loop",
            "godot-dev-loop",
            "spec-interview",
            "completion-loop",
            "visual-match",
            "handoff-memory",
            "project-chronicle",
            "github-pr-review",
            "github-pr-publish",
            "commit-helper",
        }

        groups = {plugin["name"]: plugin for plugin in manifest["plugins"]}
        expected_groups = {
            "codex": set(codex_native),
            "design": {"design-loop", "visual-match"},
            "execution": {"completion-loop"},
            "experimental": {"godot-dev-loop"},
            "git-workflow": {"commit-helper", "github-pr-review", "github-pr-publish"},
            "planning": {"spec-interview"},
            "project-memory": {"handoff-memory", "project-chronicle"},
        }
        self.assertEqual(len(groups), len(manifest["plugins"]))
        self.assertEqual(
            {name: {Path(path).name for path in group["skills"]} for name, group in groups.items()},
            expected_groups,
        )
        grouped_names = [Path(path).name for group in groups.values() for path in group["skills"]]
        self.assertEqual(len(grouped_names), len(set(grouped_names)))
        self.assertEqual(set(grouped_names), {path.parent.name for path in SKILLS.glob("*/SKILL.md")})
        codex_group = {Path(path).name for path in groups["codex"]["skills"]}
        cross_agent_group = {
            Path(path).name
            for name, group in groups.items()
            if name != "codex"
            for path in group["skills"]
        }
        self.assertEqual(codex_group, set(codex_native))
        self.assertEqual(cross_agent_group, common)
        self.assertTrue(codex_group.isdisjoint(cross_agent_group))
        for group in groups.values():
            self.assertEqual(group["source"], "./")
            for path in group["skills"]:
                self.assertTrue((REPO_ROOT / path / "SKILL.md").is_file())

        for name in codex_group:
            ui = read(f"skills/{name}/agents/openai.yaml")
            self.assertIn('display_name: "Codex · ', ui)
        for name in {"spec-interview", "completion-loop", "visual-match", "godot-dev-loop", "project-chronicle"}:
            ui = read(f"skills/{name}/agents/openai.yaml")
            metadata = read(f"skills/{name}/metadata.json")
            self.assertNotIn('display_name: "Codex · ', ui)
            self.assertIn("cross-agent", metadata.lower())

        for readme_path in ("README.md", "README.ko.md"):
            readme = read(readme_path)
            for group_name in expected_groups:
                title = group_name.replace("-", " ").title()
                self.assertIn(f"`{title}`:", readme)

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
