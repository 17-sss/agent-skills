from __future__ import annotations

from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tarfile
from types import SimpleNamespace
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = REPO_ROOT / "scripts" / "check-native-workflow-skills.py"
SPEC = importlib.util.spec_from_file_location("native_workflow_checker", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class NativeWorkflowCheckerTest(unittest.TestCase):
    def load_manifest_data(self):
        return json.loads(
            (REPO_ROOT / "docs" / "native-workflow-sources.json").read_text(
                encoding="utf-8"
            )
        )

    def validate_temporary_manifest(self, manifest):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            manifest_path = Path(temp_dir) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            original = checker.SOURCE_MANIFEST
            checker.SOURCE_MANIFEST = manifest_path
            try:
                errors = []
                with redirect_stdout(io.StringIO()):
                    result = checker.load_manifest(errors)
            finally:
                checker.SOURCE_MANIFEST = original
        return result, errors

    def test_inventory_and_manifest_mapping_are_exact(self):
        self.assertEqual(
            set(checker.SKILL_NAMES),
            {
                "spec-interview",
                "reviewed-plan",
                "completion-loop",
                "visual-match",
                "review-gate",
                "milestone-runner",
            },
        )
        self.assertIn("playwright.dev", checker.ALLOWED_REFERENCE_HOSTS)
        errors = []
        self.assertIsNotNone(checker.load_manifest(errors))
        self.assertEqual(errors, [])

    def test_manifest_rejects_missing_source_mapping(self):
        manifest = self.load_manifest_data()
        del manifest["upstream"]["skills"]["review-gate"]
        result, errors = self.validate_temporary_manifest(manifest)
        self.assertIsNone(result)
        self.assertTrue(any("skill set mismatch" in error for error in errors))

    def test_upstream_archive_matching_uses_content_fingerprints(self):
        payload = b"---\nname: source-skill\ndescription: fixture\n---\n"
        archive_bytes = io.BytesIO()
        with tarfile.open(fileobj=archive_bytes, mode="w:gz") as archive:
            member = tarfile.TarInfo("source-repo/skills/source-skill/SKILL.md")
            member.size = len(payload)
            archive.addfile(member, io.BytesIO(payload))
        archive_bytes.seek(0)

        self.assertEqual(
            checker.read_skill_hashes_from_archive(archive_bytes),
            {hashlib.sha256(payload).hexdigest()},
        )

    def test_manifest_requires_native_review_capability(self):
        manifest = self.load_manifest_data()
        manifest["codex"]["reviewed_capabilities"].remove(
            "native /review target selection and read-only review behavior"
        )
        result, errors = self.validate_temporary_manifest(manifest)
        self.assertIsNone(result)
        self.assertTrue(any("lacks reviewed Codex capabilities" in error for error in errors))

    def test_manifest_requires_evidence_for_every_native_capability(self):
        manifest = self.load_manifest_data()
        del manifest["codex"]["capability_evidence"]["Goal mode and /goal"]
        result, errors = self.validate_temporary_manifest(manifest)
        self.assertIsNone(result)
        self.assertTrue(any("Codex evidence set mismatch" in error for error in errors))

    def test_manifest_tracks_permission_and_surface_boundaries(self):
        evidence = self.load_manifest_data()["codex"]["capability_evidence"]
        self.assertIn(
            "Starting a goal doesn't grant ChatGPT broader access.",
            evidence["Goal mode and /goal"],
        )
        self.assertIn(
            "Subagents inherit your current sandbox policy.",
            evidence["native subagents"],
        )
        self.assertIn(
            "Browser isn't available in Codex CLI or the Codex IDE extension.",
            evidence["built-in Browser and Chrome extension routing"],
        )

    def test_codex_manual_evidence_detects_documentation_drift(self):
        manifest = self.load_manifest_data()
        complete_text = "\n".join(
            fragment
            for fragments in manifest["codex"]["capability_evidence"].values()
            for fragment in fragments
        )
        errors = []
        with redirect_stdout(io.StringIO()):
            checker.validate_codex_manual_text(manifest, complete_text, errors)
        self.assertEqual(errors, [])

        missing_fragment = manifest["codex"]["capability_evidence"][
            "Goal mode and /goal"
        ][0]
        errors = []
        with redirect_stdout(io.StringIO()):
            checker.validate_codex_manual_text(
                manifest,
                complete_text.replace(missing_fragment, ""),
                errors,
            )
        self.assertTrue(any("Goal mode and /goal" in error for error in errors))

    def test_catalog_rejects_implicit_invocation(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            skill_dir = Path(temp_dir) / "codex-fixture"
            (skill_dir / "agents").mkdir(parents=True)
            metadata = {
                "name": "codex-fixture",
                "version": "0.1.0",
                "organization": "17-sss",
                "date": "July 2026",
                "abstract": "Fixture metadata for checker validation.",
                "references": ["https://developers.openai.com/codex/codex-manual.md"],
            }
            (skill_dir / "metadata.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )
            (skill_dir / "agents" / "openai.yaml").write_text(
                "interface:\n"
                '  display_name: "Codex Fixture"\n'
                '  short_description: "Fixture description for validation"\n'
                '  default_prompt: "Use $codex-fixture for this fixture."\n',
                encoding="utf-8",
            )
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_catalog_files(skill_dir, errors)
        self.assertTrue(any("unexpected YAML shape" in error for error in errors))

    def test_catalog_rejects_short_description_outside_supported_length(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            skill_dir = Path(temp_dir) / "codex-fixture"
            (skill_dir / "agents").mkdir(parents=True)
            metadata = {
                "name": "codex-fixture",
                "version": "0.1.0",
                "organization": "17-sss",
                "date": "July 2026",
                "abstract": "Fixture metadata for checker validation.",
                "references": ["https://developers.openai.com/codex/codex-manual.md"],
            }
            (skill_dir / "metadata.json").write_text(
                json.dumps(metadata), encoding="utf-8"
            )
            (skill_dir / "agents" / "openai.yaml").write_text(
                "interface:\n"
                '  display_name: "Codex Fixture"\n'
                '  short_description: "Too short"\n'
                '  default_prompt: "Use $codex-fixture for this fixture."\n'
                "policy:\n"
                "  allow_implicit_invocation: false\n",
                encoding="utf-8",
            )
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_catalog_files(skill_dir, errors)
        self.assertTrue(any("25-64 characters" in error for error in errors))

    def test_frontmatter_name_requires_exact_match(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            skill_dir = Path(temp_dir)
            (skill_dir / "SKILL.md").write_text(
                "---\n"
                f"name: {skill_dir.name}-extra\n"
                "description: Fixture description.\n"
                "---\n",
                encoding="utf-8",
            )
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_frontmatter(skill_dir, errors)
        self.assertTrue(any("name does not match" in error for error in errors))

    def test_runtime_independence_scans_default_prompt(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            skill_dir = Path(temp_dir)
            (skill_dir / "agents").mkdir()
            (skill_dir / "SKILL.md").write_text("safe", encoding="utf-8")
            (skill_dir / "agents" / "openai.yaml").write_text(
                'default_prompt: "Run omx state now"\n', encoding="utf-8"
            )
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_runtime_independence(skill_dir, errors)
        self.assertTrue(any("banned runtime name" in error for error in errors))

    def test_runtime_independence_scans_scripts_metadata_and_nested_references(self):
        fixtures = (
            ("scripts/run.py", "print('start tmux')\n", "terminal multiplexer"),
            ("metadata.json", '{"runtime": "omx"}\n', "runtime name"),
            (
                "metadata.json",
                '{"source": "https://github.com/example/oh-my-codex"}\n',
                "legacy workflow provenance",
            ),
            (
                "references/nested/lifecycle.md",
                "Register a UserPromptSubmit callback.\n",
                "runtime lifecycle hook",
            ),
        )
        for relative_path, content, expected_label in fixtures:
            with self.subTest(relative_path=relative_path):
                with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
                    skill_dir = Path(temp_dir)
                    target = skill_dir / relative_path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(content, encoding="utf-8")
                    errors = []
                    with redirect_stdout(io.StringIO()):
                        checker.validate_runtime_independence(skill_dir, errors)
                self.assertTrue(
                    any(expected_label in error for error in errors),
                    errors,
                )

    def test_runtime_independence_rejects_package_symlinks(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            skill_dir = Path(temp_dir)
            target = skill_dir / "outside.txt"
            target.write_text("safe\n", encoding="utf-8")
            link = skill_dir / "linked.txt"
            link.symlink_to(target)
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_runtime_independence(skill_dir, errors)
        self.assertTrue(any("must be self-contained" in error for error in errors))

    def test_runtime_independence_rejects_symlinked_package_root(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            fixture_root = Path(temp_dir)
            target = fixture_root / "real-package"
            target.mkdir()
            link = fixture_root / "linked-package"
            link.symlink_to(target, target_is_directory=True)
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_runtime_independence(link, errors)
        self.assertTrue(any("must be self-contained" in error for error in errors))

    def test_standalone_package_rejects_sibling_skill_dependencies(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            skill_dir = Path(temp_dir)
            (skill_dir / "SKILL.md").write_text(
                "Invoke $completion-loop before continuing.\n",
                encoding="utf-8",
            )
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_standalone_package(skill_dir, errors)
        self.assertTrue(any("references sibling skill completion-loop" in error for error in errors))

    def test_milestone_runner_state_contract_uses_shared_namespace(self):
        errors = []
        with redirect_stdout(io.StringIO()):
            checker.validate_state_contract(
                REPO_ROOT / "skills" / "milestone-runner",
                errors,
            )
        self.assertEqual(errors, [])

    def test_state_contract_rejects_native_goal_calls_in_helper(self):
        for goal_call in ("create_goal", "get_goal", "update_goal"):
            with self.subTest(goal_call=goal_call):
                with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
                    skill_dir = Path(temp_dir) / "milestone-runner"
                    (skill_dir / "references").mkdir(parents=True)
                    (skill_dir / "scripts").mkdir()
                    (skill_dir / "SKILL.md").write_text(
                        ".agent-workflows/goals/<slug>/ pending transaction\n",
                        encoding="utf-8",
                    )
                    (skill_dir / "references" / "state-contract.md").write_text(
                        ".agent-workflows/ .pending-transaction.json "
                        "implementation_changed\n",
                        encoding="utf-8",
                    )
                    (skill_dir / "scripts" / "goal_state.py").write_text(
                        'STATE_DIRECTORY = ".agent-workflows"\n'
                        'TRANSACTION_FILE = ".pending-transaction.json"\n'
                        "def validate_projection(): pass\n"
                        f"{goal_call}()\n",
                        encoding="utf-8",
                    )
                    errors = []
                    with redirect_stdout(io.StringIO()):
                        checker.validate_state_contract(skill_dir, errors)
                self.assertTrue(
                    any(
                        f"must not call native goal tool {goal_call}" in error
                        for error in errors
                    )
                )

    def test_milestone_runner_state_contract_rejects_missing_markers_and_alt_roots(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            skill_dir = Path(temp_dir) / "milestone-runner"
            (skill_dir / "references").mkdir(parents=True)
            (skill_dir / "scripts").mkdir()
            (skill_dir / "SKILL.md").write_text(
                ".agent-workflows/goals/<slug>/\n",
                encoding="utf-8",
            )
            (skill_dir / "references" / "state-contract.md").write_text(
                ".agent-workflows/ .pending-transaction.json implementation_changed\n",
                encoding="utf-8",
            )
            (skill_dir / "scripts" / "goal_state.py").write_text(
                'STATE_DIRECTORY = ".agent-workflows"\n'
                'TRANSACTION_FILE = ".pending-transaction.json"\n'
                'ALT_STATE = ".codex/workflows"\n'
                "def validate_projection(): pass\n",
                encoding="utf-8",
            )
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_state_contract(skill_dir, errors)
        self.assertTrue(any("lacks state-contract marker 'pending transaction'" in e for e in errors))
        self.assertTrue(any("alternate mutable state roots" in error for error in errors))

    def test_bundled_scripts_must_be_executable(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            skill_dir = Path(temp_dir)
            scripts = skill_dir / "scripts"
            scripts.mkdir()
            script = scripts / "helper.py"
            script.write_text("print('safe')\n", encoding="utf-8")
            script.chmod(0o644)
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_bundled_scripts(skill_dir, errors)
        self.assertTrue(any("must be executable" in error for error in errors))

    def test_non_milestone_runner_package_cannot_create_shared_state(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            skill_dir = Path(temp_dir)
            (skill_dir / "SKILL.md").write_text(
                "Write .agent-workflows/goals/state.json.\n",
                encoding="utf-8",
            )
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_state_contract(skill_dir, errors)
        self.assertTrue(any("unnecessary shared workflow state" in error for error in errors))

    def test_explicit_validator_path_is_portable_and_checked(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT) as temp_dir:
            validator = Path(temp_dir) / "quick_validate.py"
            validator.write_text("print('ok')\n", encoding="utf-8")
            self.assertEqual(checker.find_skill_validator(str(validator)), validator)
            self.assertIsNone(
                checker.find_skill_validator(str(Path(temp_dir) / "missing.py"))
            )

    def test_validator_python_uses_path_discovery_before_fixed_fallback(self):
        portable_python = "/portable/bin/python3"

        def fake_run(command, **_kwargs):
            return SimpleNamespace(returncode=0 if command[0] == portable_python else 1)

        def fake_which(name):
            return portable_python if name == "python3" else None

        with mock.patch.object(checker.shutil, "which", side_effect=fake_which), mock.patch.object(
            checker.subprocess,
            "run",
            side_effect=fake_run,
        ):
            self.assertEqual(checker.find_validator_python(None), portable_python)

    def test_package_links_cannot_escape_installable_root(self):
        with tempfile.TemporaryDirectory(dir=REPO_ROOT / "skills") as temp_dir:
            fixture_root = Path(temp_dir)
            skill_dir = fixture_root / "codex-fixture"
            skill_dir.mkdir()
            outside = fixture_root / "outside.md"
            outside.write_text("outside\n", encoding="utf-8")
            readme = skill_dir / "README.md"
            readme.write_text("[escape](../outside.md)\n", encoding="utf-8")
            errors = []
            with redirect_stdout(io.StringIO()):
                checker.validate_markdown_links(
                    readme,
                    errors,
                    allowed_root=skill_dir,
                )
        self.assertTrue(any("outside its installable root" in error for error in errors))

    def test_missing_package_reports_errors_without_crashing(self):
        missing = REPO_ROOT / "skills" / "codex-missing-fixture"
        errors = []
        with redirect_stdout(io.StringIO()):
            checker.validate_frontmatter(missing, errors)
            checker.validate_runtime_independence(missing, errors)
            checker.validate_links(missing, errors)
            checker.validate_catalog_files(missing, errors)
        self.assertTrue(any("SKILL.md is missing" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
