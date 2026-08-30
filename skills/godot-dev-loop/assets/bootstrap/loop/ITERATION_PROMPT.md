# Disposable Game-Development Iteration

You are exactly one disposable game-development iteration. You have no reliable memory of earlier sessions.

Read in this order:

1. `docs/feedback/INBOX.md`
2. `docs/DESIGN.md`
3. `docs/STATUS.md`

Then inspect the current repository and Git state as needed. The repository and these canonical files are the source of truth; do not rely on conversation memory.

Choose the highest-priority unfinished task that can be meaningfully advanced as one coherent improvement in this iteration. Respect the latest human directive, the durable game contract, the ordered queue, unrelated work, and existing repository instructions. Do not broaden scope merely because you notice another opportunity.

Implement the improvement and run the smallest relevant functional checks. Select an explicit relevant state from `qa/visual-qa/godot/states.json`, then run:

```bash
GAME_START=<state> ./scripts/game-capture.sh
```

The capture must launch Godot through the normal non-headless real-window path. Open and inspect the newly captured PNG yourself with an actual local-image capability before judging the result. A build, source inspection, or PNG existence alone is not visual verification.

If the rendered result exposes a material problem related to this work, repair it and recapture. Keep repairs bounded to the current improvement and any regression it caused.

Before exiting, rewrite `docs/STATUS.md` as a compact handoff for a completely fresh next agent. Record current playable truth, the latest functional evidence, GAME_START, PNG and sidecar paths, whether the PNG was actually inspected, material problems, ordered next actions, feedback disposition, completed capabilities, and unresolved blockers or risks. Do not append a session transcript. Do not delete user-authored INBOX directives.

If progress requires a material user decision, Godot 4.x or the graphical session is unavailable, capture fails without a new correction path, or you cannot inspect the local image, update STATUS and write `loop/BLOCKED` with a short concrete reason.

If every `docs/DESIGN.md` good-enough criterion is satisfied with current functional and inspected visual evidence, update STATUS and write `loop/STOP` with a short completion reason. Do not continue polishing after the stop contract is met.

Exit after this one bounded iteration. Do not resume or reconnect to an earlier agent conversation.
