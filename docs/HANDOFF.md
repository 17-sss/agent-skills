# HANDOFF

## Metadata

- Project: agent-skills
- Project ID: git-github.com-17-sss-17-sss-agent-skills
- Repo Root: `.`
- Branch: main
- Last Updated: 2026-08-30
- Updated By: Codex

## TL;DR

- `godot-dev-loop` is implemented and committed locally at `cd0a43c`; it has not been pushed.
- Offline bootstrap, state-resolution, loop-safety, catalog, and package validation pass.
- A real Godot 4 window capture and inspection are still unverified because the current Ubuntu SSH/TTY environment has no Godot executable and no graphical display session.

## Current Objective

- Run the capability-gated Godot 4 smoke test on a machine with a real graphical session, inspect the generated PNG, and update the public verification status from evidence.

## Current State

- Done: the standalone `skills/godot-dev-loop/` package, Godot 4 bootstrap templates, deterministic `GAME_START` registry, real-window capture command, fresh Claude/Codex/custom runners, STOP/BLOCKED handling, tests, and catalog registration.
- Done: `skills/godot-dev-loop/README.md` explicitly labels the live visual smoke test as capability-gated and unverified.
- Pending confirmation: actual Godot `--import`, normal non-headless window launch, `RenderingServer.frame_post_draw` capture, non-empty PNG and JSON sidecar creation, automatic exit, and human/agent image inspection.
- Repository state at handoff creation: `main` is ahead of `origin/main`; no push is authorized by this handoff.

## Recent Changes

- Change: added `godot-dev-loop` as a cross-agent `Other` skill, then renamed it from the tentative `game-dev-loop` name before publication.
- Validation: repository tests exercise bootstrap generation, preservation of existing files, Git-root handling, Bash syntax, alias rejection, stubbed Godot command arguments, runner isolation, and failure cutoffs without requiring a graphical Godot installation.
- Impact: the package is ready for catalog publication except for the explicitly recorded live-render verification gap.

## Known Issues / Watch List

- Issue: no `godot4`, `godot`, `godot4.exe`, or `godot.exe` executable was found in the current environment; both `DISPLAY` and `WAYLAND_DISPLAY` are unset.
- Risk: source and stubbed process checks cannot prove that Godot creates the intended real window, captures a correct rendered frame, or produces visually valid evidence.
- Workaround: use any macOS, Windows-with-Bash, or Linux desktop session that can run Godot 4 and inspect a local PNG. Do not use `--headless`, a placeholder image, or PNG existence alone as a substitute.

## Quick Reference

- Key files: `skills/godot-dev-loop/SKILL.md`, `skills/godot-dev-loop/README.md`, `skills/godot-dev-loop/references/godot4-visual-qa.md`, `tests/test_godot_dev_loop.py`.
- Bootstrap command: `python3 skills/godot-dev-loop/scripts/bootstrap_godot_dev_loop.py <temporary-godot-project> --game <concept> --core-loop <loop> --good-enough <observable-stop-condition>`.
- Live capture command inside the temporary target project: `GAME_START=smoke bash scripts/game-capture.sh`.
- Evidence to retain while verifying: command output, generated `artifacts/visual/*.png`, matching `*.png.json`, and the result of opening and visually inspecting that PNG.

## Validation

- Checks run: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`.
- Checks run: `python3 scripts/check-native-workflow-skills.py --require-validator`.
- Checks run: `npx --yes skills add . --list`.
- Results: all 105 unit tests passed; the native workflow checker passed; the skills CLI listed 13 skills with `godot-dev-loop` under `Other`.
- Not run yet: an actual Godot 4 graphical smoke capture and inspection. This remains unverified, not failed.

## Next Actions

1. On a graphical machine, clone or update this repository and verify the checkout contains `cd0a43c` plus this documentation commit.
2. Create a disposable Godot 4 project outside this catalog repository, run the bootstrap helper with a complete three-part game brief, then run `GAME_START=smoke bash scripts/game-capture.sh` from that target project.
3. Confirm there was one explicit import pass followed by a normal non-headless window run, the process closed itself, and a non-empty PNG plus JSON sidecar were written.
4. Open and inspect the newly generated PNG with a real image-capable tool. Record visible correctness or defects; do not infer visual success from file existence.
5. Update `skills/godot-dev-loop/README.md` and this HANDOFF with the observed result. If successful, replace the capability-gated warning with the tested platform and evidence; if unsuccessful, preserve the failure output and record the blocker.

## Resume Checklist

- Run `git status --short --branch` and compare `HEAD` with the commits named above.
- Re-open the four Quick Reference files and confirm the live test remains marked unverified.
- Confirm Godot reports major version 4 and the session has a usable graphical display before bootstrapping the disposable target project.
- Keep the catalog repository itself separate from the temporary Godot project.

## Resume Prompt

Continue the `godot-dev-loop` live-verification work from `docs/HANDOFF.md`. First compare the current branch, commits, and public verification note with the handoff. If a real graphical session, Godot 4, Bash, and local image inspection are available, execute the first unfinished Next Action using a disposable Godot project outside this catalog repository. Do not claim visual success until you open and inspect the newly captured PNG, and do not push unless the user separately authorizes it.
