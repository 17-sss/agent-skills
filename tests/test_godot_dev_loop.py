from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "godot-dev-loop"
BOOTSTRAP = SKILL_ROOT / "scripts" / "bootstrap_godot_dev_loop.py"
BRIEF_ARGS = (
    "--game",
    "A compact tactical dungeon crawler",
    "--core-loop",
    "Explore, choose an encounter, resolve it, and improve the party",
    "--good-enough",
    "The smoke and dungeon states render and one encounter is winnable",
)


def write_fixture_project(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    (path / "project.godot").write_text(
        '[application]\nconfig/name="Fixture"\n\n'
        "[display]\nwindow/size/viewport_width=640\n"
        "window/size/viewport_height=360\n\n"
        '[rendering]\nrenderer/rendering_method="gl_compatibility"\n',
        encoding="utf-8",
    )


def bootstrap(project: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(BOOTSTRAP), str(project), *extra, "--format", "json"],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


class GodotDevLoopTest(unittest.TestCase):
    def test_package_is_standalone_and_contains_core_contracts(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        prompt = (SKILL_ROOT / "assets/bootstrap/loop/ITERATION_PROMPT.md").read_text(
            encoding="utf-8"
        )
        harness = (
            SKILL_ROOT
            / "assets/bootstrap/qa/visual-qa/godot/capture_harness.gd"
        ).read_text(encoding="utf-8")
        capture = (
            SKILL_ROOT / "assets/bootstrap/scripts/game-capture.sh"
        ).read_text(encoding="utf-8")
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted(SKILL_ROOT.rglob("*"))
            if path.is_file()
        )

        self.assertIn("What game are we making?", skill)
        self.assertIn("What is the core gameplay loop?", skill)
        self.assertIn("good enough to stop iterating", skill)
        self.assertIn("docs/feedback/INBOX.md", prompt)
        self.assertLess(
            prompt.index("docs/feedback/INBOX.md"), prompt.index("docs/DESIGN.md")
        )
        self.assertLess(prompt.index("docs/DESIGN.md"), prompt.index("docs/STATUS.md"))
        self.assertIn("await RenderingServer.frame_post_draw", harness)
        self.assertIn("image.save_png(capture_path)", harness)
        self.assertIn("get_tree().quit(0)", harness)
        self.assertEqual(capture.count("--import"), 1)
        self.assertIn('"$godot_bin" --path "$PROJECT_ROOT" --scene', capture)
        self.assertNotIn(
            '"$godot_bin" --headless --path "$PROJECT_ROOT" --scene', capture
        )
        for sibling in (
            "design-loop",
            "visual-match",
            "handoff-memory",
            "spec-interview",
            "completion-loop",
            "reviewed-plan",
            "milestone-runner",
            "review-gate",
            "project-chronicle",
            "github-pr-review",
            "github-pr-publish",
            "commit-helper",
        ):
            self.assertNotIn(sibling, combined)

    def test_bootstrap_creates_complete_project_local_workflow_and_git(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "game"
            write_fixture_project(project)
            original_project = (project / "project.godot").read_bytes()

            result = bootstrap(project, *BRIEF_ARGS)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["git_action"], "initialized")
            self.assertEqual(Path(report["git_root"]), project.resolve())
            self.assertTrue((project / ".git").is_dir())
            self.assertEqual((project / "project.godot").read_bytes(), original_project)

            expected = (
                "docs/DESIGN.md",
                "docs/STATUS.md",
                "docs/feedback/INBOX.md",
                "loop/ITERATION_PROMPT.md",
                "loop/loop.sh",
                "loop/runners/claude.sh",
                "loop/runners/codex.sh",
                "scripts/game-capture.sh",
                "scripts/validate-game-design.py",
                "qa/visual-qa/godot/capture_harness.gd",
                "qa/visual-qa/godot/capture_harness.tscn",
                "qa/visual-qa/godot/resolve_game_state.py",
                "qa/visual-qa/godot/smoke_state.tscn",
                "qa/visual-qa/godot/states.json",
            )
            for relative in expected:
                self.assertTrue((project / relative).is_file(), relative)
            self.assertTrue((project / "artifacts/visual").is_dir())
            self.assertTrue((project / "loop/logs").is_dir())
            self.assertIn("/loop/STOP", (project / ".gitignore").read_text(encoding="utf-8"))
            self.assertIn(
                "## Good Enough / Stop Criteria",
                (project / "docs/DESIGN.md").read_text(encoding="utf-8"),
            )
            self.assertTrue(os.access(project / "loop/loop.sh", os.X_OK))
            self.assertTrue(os.access(project / "scripts/game-capture.sh", os.X_OK))

    def test_bootstrap_requires_the_three_answer_brief_before_writing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "game"
            write_fixture_project(project)
            result = bootstrap(project)
            self.assertEqual(result.returncode, 2)
            self.assertIn("answer the brief gate", result.stderr)
            self.assertIn("--game", result.stderr)
            self.assertIn("--core-loop", result.stderr)
            self.assertIn("--good-enough", result.stderr)
            self.assertFalse((project / ".git").exists())
            self.assertFalse((project / "docs").exists())

    def test_bootstrap_reuses_enclosing_git_repository_without_nesting(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            outer = Path(temp_dir) / "outer"
            outer.mkdir()
            init = subprocess.run(
                ["git", "init", "-q", str(outer)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(init.returncode, 0, init.stderr)
            project = outer / "games" / "fixture"
            write_fixture_project(project)

            result = bootstrap(project, *BRIEF_ARGS)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["git_action"], "reused")
            self.assertEqual(Path(report["git_root"]), outer.resolve())
            self.assertFalse((project / ".git").exists())

    def test_bootstrap_preserves_existing_state_and_rejects_qa_conflicts(self):
        valid_design = """# Existing Design

## Game Concept
Existing concept.

## Core Gameplay Loop
Existing loop.

## Good Enough / Stop Criteria
Existing observable stop.
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "preserve"
            write_fixture_project(project)
            (project / "docs/feedback").mkdir(parents=True)
            sentinels = {
                "docs/DESIGN.md": valid_design,
                "docs/STATUS.md": "existing status\n",
                "docs/feedback/INBOX.md": "human directive\n",
            }
            for relative, content in sentinels.items():
                (project / relative).write_text(content, encoding="utf-8")

            result = bootstrap(project, "--accept-existing-design")
            self.assertEqual(result.returncode, 0, result.stderr)
            for relative, content in sentinels.items():
                self.assertEqual((project / relative).read_text(encoding="utf-8"), content)

        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "conflict"
            write_fixture_project(project)
            (project / "scripts").mkdir()
            (project / "scripts/game-capture.sh").write_text(
                "existing project capture\n", encoding="utf-8"
            )

            result = bootstrap(project, *BRIEF_ARGS)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("bootstrap conflicts detected", result.stderr)
            self.assertFalse((project / ".git").exists())
            self.assertFalse((project / "docs/DESIGN.md").exists())
            self.assertEqual(
                (project / "scripts/game-capture.sh").read_text(encoding="utf-8"),
                "existing project capture\n",
            )

    def test_bootstrap_is_deterministic_and_generated_bash_is_valid(self):
        if shutil.which("bash") is None:
            self.skipTest("bash is unavailable")
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "game"
            write_fixture_project(project)
            first = bootstrap(project, *BRIEF_ARGS)
            self.assertEqual(first.returncode, 0, first.stderr)
            tracked = [
                path
                for path in project.rglob("*")
                if path.is_file() and ".git" not in path.parts and path.name != ".gitignore"
            ]
            before = {
                path.relative_to(project).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in tracked
            }
            ignore_before = (project / ".gitignore").read_bytes()

            second = bootstrap(project, "--accept-existing-design")
            self.assertEqual(second.returncode, 0, second.stderr)
            after = {
                path.relative_to(project).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in tracked
            }
            self.assertEqual(after, before)
            self.assertEqual((project / ".gitignore").read_bytes(), ignore_before)
            for script in (
                project / "loop/loop.sh",
                project / "loop/runners/claude.sh",
                project / "loop/runners/codex.sh",
                project / "scripts/game-capture.sh",
            ):
                check = subprocess.run(
                    ["bash", "-n", str(script)],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(check.returncode, 0, f"{script}: {check.stderr}")

    def test_state_resolver_accepts_alias_and_direct_scene_and_rejects_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "game"
            write_fixture_project(project)
            result = bootstrap(project, *BRIEF_ARGS)
            self.assertEqual(result.returncode, 0, result.stderr)
            resolver = project / "qa/visual-qa/godot/resolve_game_state.py"

            alias = subprocess.run(
                [sys.executable, str(resolver), "--project-root", str(project), "--state", "smoke"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(alias.returncode, 0, alias.stderr)
            self.assertEqual(
                alias.stdout.strip().split("\t")[:2],
                ["smoke", "res://qa/visual-qa/godot/smoke_state.tscn"],
            )

            direct_scene = project / "scenes" / "dungeon.tscn"
            direct_scene.parent.mkdir()
            direct_scene.write_text("[gd_scene format=3]\n", encoding="utf-8")
            direct = subprocess.run(
                [
                    sys.executable,
                    str(resolver),
                    "--project-root",
                    str(project),
                    "--state",
                    "res://scenes/dungeon.tscn",
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(direct.returncode, 0, direct.stderr)
            self.assertIn("res://scenes/dungeon.tscn", direct.stdout)

            unknown = subprocess.run(
                [sys.executable, str(resolver), "--project-root", str(project), "--state", "dungeon"],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(unknown.returncode, 2)
            self.assertIn("unknown GAME_START alias", unknown.stderr)
            self.assertIn("known aliases: smoke", unknown.stderr)

    def test_capture_script_uses_one_import_then_non_headless_render(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "game with spaces"
            write_fixture_project(project)
            result = bootstrap(project, *BRIEF_ARGS)
            self.assertEqual(result.returncode, 0, result.stderr)
            fake_godot = project / "fake godot"
            log = project / "godot-argv.log"
            write_executable(
                fake_godot,
                """#!/usr/bin/env bash
set -euo pipefail
printf '%s\\n' "$*" >> "$GODOT_LOG"
if [[ "${1:-}" == "--version" ]]; then
  printf '4.4.1.stable.fixture\\n'
  exit 0
fi
if [[ " $* " == *" --scene "* ]]; then
  printf 'fixture-png' > "$GAME_CAPTURE_PATH"
  printf '{"fixture":true}\\n' > "$GAME_CAPTURE_PATH.json"
fi
""",
            )
            env = os.environ.copy()
            env.update(
                {
                    "DISPLAY": ":99",
                    "GODOT_BIN": str(fake_godot),
                    "GODOT_LOG": str(log),
                    "GAME_START": "smoke",
                    "GAME_CAPTURE_OUTPUT": "artifacts/visual/test-smoke.png",
                }
            )
            capture = subprocess.run(
                ["bash", str(project / "scripts/game-capture.sh")],
                cwd=project,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(capture.returncode, 0, capture.stderr)
            calls = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[0], "--version")
            self.assertIn("--headless", calls[1])
            self.assertIn("--import", calls[1])
            self.assertNotIn("--scene", calls[1])
            self.assertIn("--scene", calls[2])
            self.assertNotIn("--headless", calls[2])
            self.assertTrue((project / "artifacts/visual/test-smoke.png").is_file())
            self.assertTrue((project / "artifacts/visual/test-smoke.png.json").is_file())

            env["GAME_START"] = "unknown"
            log.unlink()
            unknown = subprocess.run(
                ["bash", str(project / "scripts/game-capture.sh")],
                cwd=project,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(unknown.returncode, 0)
            self.assertIn("unknown GAME_START alias", unknown.stderr)
            self.assertNotIn("--import", log.read_text(encoding="utf-8"))

            env.pop("DISPLAY", None)
            env.pop("WAYLAND_DISPLAY", None)
            env["GAME_START"] = "smoke"
            log.unlink()
            no_display = subprocess.run(
                ["bash", str(project / "scripts/game-capture.sh")],
                cwd=project,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            if sys.platform.startswith(("linux", "freebsd")):
                self.assertEqual(no_display.returncode, 3)
                self.assertIn("real-window visual QA is unavailable", no_display.stderr)
                self.assertFalse(log.exists())

    def test_loop_honors_stop_blocked_and_runner_failure_cutoff(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "terminal"
            write_fixture_project(project)
            result = bootstrap(project, *BRIEF_ARGS)
            self.assertEqual(result.returncode, 0, result.stderr)
            adapter = project / "adapter.sh"
            marker = project / "adapter-ran"
            write_executable(adapter, f"#!/usr/bin/env bash\ntouch {str(marker)!r}\n")
            env = os.environ.copy()
            env.update({"GODOT_DEV_RUNNER": str(adapter), "GODOT_DEV_ITERATION_DELAY_SECONDS": "0"})

            (project / "loop/STOP").write_text("done\n", encoding="utf-8")
            stopped = subprocess.run(
                ["bash", str(project / "loop/loop.sh")],
                cwd=project,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(stopped.returncode, 0)
            self.assertFalse(marker.exists())
            (project / "loop/STOP").unlink()

            (project / "loop/BLOCKED").write_text("needs display\n", encoding="utf-8")
            blocked = subprocess.run(
                ["bash", str(project / "loop/loop.sh")],
                cwd=project,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(blocked.returncode, 2)
            self.assertFalse(marker.exists())

        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "cutoff"
            write_fixture_project(project)
            result = bootstrap(project, *BRIEF_ARGS)
            self.assertEqual(result.returncode, 0, result.stderr)
            adapter = project / "failing-adapter.sh"
            counter = project / "calls.log"
            write_executable(
                adapter,
                f"#!/usr/bin/env bash\nprintf 'call\\n' >> {str(counter)!r}\nexit 9\n",
            )
            env = os.environ.copy()
            env.update(
                {
                    "GODOT_DEV_RUNNER": str(adapter),
                    "GODOT_DEV_MAX_RUNNER_FAILURES": "2",
                    "GODOT_DEV_ITERATION_DELAY_SECONDS": "0",
                }
            )
            cutoff = subprocess.run(
                ["bash", str(project / "loop/loop.sh")],
                cwd=project,
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(cutoff.returncode, 2)
            self.assertEqual(counter.read_text(encoding="utf-8").splitlines(), ["call", "call"])
            self.assertIn(
                "failed 2 consecutive times",
                (project / "loop/BLOCKED").read_text(encoding="utf-8"),
            )

    def test_built_in_runners_use_fresh_noninteractive_argv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir) / "game"
            write_fixture_project(project)
            result = bootstrap(project, *BRIEF_ARGS)
            self.assertEqual(result.returncode, 0, result.stderr)
            prompt = project / "loop/ITERATION_PROMPT.md"

            claude_log = project / "claude.log"
            fake_claude = project / "fake-claude"
            write_executable(
                fake_claude,
                "#!/usr/bin/env bash\nprintf '%s\\n' \"$@\" > \"$ADAPTER_LOG\"\n",
            )
            env = os.environ.copy()
            env.update({"CLAUDE_BIN": str(fake_claude), "ADAPTER_LOG": str(claude_log)})
            claude = subprocess.run(
                [str(project / "loop/runners/claude.sh"), str(project), str(prompt)],
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(claude.returncode, 0, claude.stderr)
            claude_args = claude_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(claude_args[:2], ["--print", "--no-session-persistence"])
            self.assertEqual(
                "\n".join(claude_args[2:]),
                prompt.read_text(encoding="utf-8").rstrip("\n"),
            )
            self.assertFalse({"--continue", "--resume", "--session-id"} & set(claude_args))

            codex_log = project / "codex.log"
            codex_stdin = project / "codex.stdin"
            fake_codex = project / "fake-codex"
            write_executable(
                fake_codex,
                """#!/usr/bin/env bash
printf '%s\\n' "$@" > "$ADAPTER_LOG"
cat > "$ADAPTER_STDIN"
""",
            )
            env.update(
                {
                    "CODEX_BIN": str(fake_codex),
                    "ADAPTER_LOG": str(codex_log),
                    "ADAPTER_STDIN": str(codex_stdin),
                }
            )
            codex = subprocess.run(
                [str(project / "loop/runners/codex.sh"), str(project), str(prompt)],
                env=env,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(codex.returncode, 0, codex.stderr)
            codex_args = codex_log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(codex_args, ["exec", "-C", str(project.resolve()), "-"])
            self.assertEqual(codex_stdin.read_text(encoding="utf-8"), prompt.read_text(encoding="utf-8"))
            self.assertNotIn("resume", codex_args)
            self.assertFalse(any("bypass" in arg or "danger" in arg for arg in codex_args))


if __name__ == "__main__":
    unittest.main()
