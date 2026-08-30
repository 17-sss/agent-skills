---
name: godot-dev-loop
description: Bootstrap and run durable, fresh-agent game-development iterations for Godot 4.x projects using a concise game brief, deterministic scene entry, real-window PNG capture, native image inspection, and bounded STOP/BLOCKED handoffs. Use for long-running playable-game work that must survive disposable agent sessions and verify rendered evidence; do not use for non-Godot engines or code-only game review.
---

# Godot Development Loop

Build and refine a playable game through this evidence chain:

`brief -> bootstrap observability -> read durable state -> improve -> run -> capture -> inspect -> repair -> hand off -> exit -> fresh process`

The repository is the memory. Every automated iteration is bounded, starts in a new non-interactive agent process, and assumes no conversation history.

## Keep the package standalone

- Do not require, install, invoke, or delegate the workflow to another skill.
- The core contract is agent-neutral. Claude Code and Codex are optional runner adapters, not runtime requirements.
- V1 supports Godot 4.x only. Do not claim Unity, Unreal, browser-game, virtual-display, or headless visual support.
- Do not make commits, push, publish, install Godot, or change external systems unless separately authorized.

## Establish the design contract first

On first use, inspect the target project and any authoritative game-design document. Before game implementation, make sure these three answers are known:

1. What game are we making?
2. What is the core gameplay loop?
3. What observable condition means the game or playable slice is good enough to stop iterating?

Reuse complete authoritative answers instead of asking again. Ask additional questions only when a missing decision would materially change implementation or acceptance. Do not turn this into a long interview.

Establish `docs/DESIGN.md` before autonomous work. It should be concise and execution-ready, normally covering the concept, intended player experience, core loop, current playable-slice target, known visual direction, constraints, non-goals, stop criteria, and material user decisions. Do not start the loop while the file is missing, fails its required-section validation, or contains unresolved placeholders.

Read [project-state-contract.md](references/project-state-contract.md) when establishing or updating the three canonical state files.

## Bootstrap a target Godot project

Confirm the target contains `project.godot`, then run the bundled helper from the installed skill directory:

```bash
python3 scripts/bootstrap_godot_dev_loop.py /path/to/game \
  --game "<game concept>" \
  --core-loop "<repeatable player loop>" \
  --good-enough "<observable stop condition>"
```

Optional arguments record player fantasy, playable-slice target, visual direction, constraints, and non-goals. If a complete canonical `docs/DESIGN.md` already exists, inspect it and use `--accept-existing-design`; the helper preserves it and validates the required sections.

The helper:

- checks `git rev-parse --show-toplevel` before considering `git init`;
- reuses an enclosing worktree instead of creating a nested repository;
- initializes Git only when the project is genuinely outside any repository;
- creates missing workflow, runner, state, and Godot QA files without silently overwriting existing files;
- leaves the real project main scene unchanged; and
- adds only a marked ignore block for transient captures, loop logs, STOP, and BLOCKED.

Resolve reported conflicts deliberately. Do not bypass them by deleting target-project files.

## Prove visual observability before iteration

Read [godot4-visual-qa.md](references/godot4-visual-qa.md), then:

1. Add or confirm explicit aliases in `qa/visual-qa/godot/states.json`.
2. Run the bootstrap state first when no playable scene exists:

   ```bash
   GAME_START=smoke ./scripts/game-capture.sh
   ```

3. Confirm the operation performs one explicit Godot import pass and then launches the capture scene through a normal, non-headless Godot window.
4. Inspect the newly written PNG through the current runtime's actual local-image capability.
5. Confirm the matching JSON sidecar records the requested state, resolved scene, PNG path, and capture time.

Visual QA is ready only after the real window launches, a rendered frame is captured, PNG saving succeeds, the process exits automatically, and the current agent actually inspects the image. Script parsing or file existence alone is insufficient.

If Godot 4.x, a graphical display, capture, or local-image inspection is unavailable, update `docs/STATUS.md`, write `loop/BLOCKED` with the concrete reason, and do not start autonomous visual iteration. Never substitute `--headless`, a placeholder image, or source inspection for this gate.

## Execute one bounded iteration

Each iteration must:

1. Read `docs/feedback/INBOX.md`.
2. Read `docs/DESIGN.md`.
3. Read `docs/STATUS.md`.
4. Inspect current repository and Git state as needed.
5. Choose the highest-priority incomplete task that can be advanced as one coherent batch.
6. Implement only that batch.
7. Run the smallest relevant functional checks.
8. Run `GAME_START=<relevant-state> ./scripts/game-capture.sh`.
9. Inspect the new PNG itself before judging the result.
10. Repair and recapture if this work produced or exposed a material visual defect.
11. Update `docs/STATUS.md` as current truth for a completely fresh agent.
12. Exit.

Do not make every edit its own iteration or absorb unrelated cleanup. Treat INBOX as the latest human override, DESIGN as the durable product contract, and STATUS as current execution state. Do not delete fulfilled INBOX directives; record their disposition in STATUS. When an INBOX directive intentionally changes the product contract, update DESIGN and record the change.

When the stop criteria are fully satisfied, write `loop/STOP` with a short reason and finish. When safe progress cannot continue, write `loop/BLOCKED` with the reason and update STATUS. Repeated capture or technical failures without a new correction path are blockers, not permission to cycle indefinitely.

## Launch disposable fresh-agent iterations

Read [fresh-runner-contract.md](references/fresh-runner-contract.md), choose a runner, and start the Bash loop explicitly:

```bash
GODOT_DEV_RUNNER=codex ./loop/loop.sh
# or
GODOT_DEV_RUNNER=claude ./loop/loop.sh
# or an executable adapter path
GODOT_DEV_RUNNER=./my-runner-adapter ./loop/loop.sh
```

`loop/loop.sh` waits for each process to exit before starting the next one. It stops for `loop/STOP`, `loop/BLOCKED`, an optional iteration limit, or the consecutive runner-failure cutoff. Its portability target is Bash on macOS, Linux, and compatible Unix-like environments; it is not a native CMD or PowerShell script.

The built-in adapters inherit the user's current permissions and configuration. They do not use permission-bypass flags, resume operations, continuation flags, or prior session identifiers. If non-interactive execution cannot proceed under the existing configuration, fail clearly and block instead of escalating permissions.

## Finish honestly

Report:

- current playable result and bounded improvement completed;
- functional checks run;
- captured state, PNG path, and whether it was actually inspected;
- STATUS, STOP, or BLOCKED outcome;
- remaining queue and material risks; and
- any capability-gated check that was not exercised.

Never claim visual acceptance from code inspection, a successful build, or a PNG that no image-capable runtime inspected.
