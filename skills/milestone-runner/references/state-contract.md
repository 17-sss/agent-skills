# Durable state contract

`milestone-runner` is the only writer of its plan state. Keep state inside the target repository so a later Codex task can resume from reviewable artifacts without depending on a global installation directory.

## Directory

```text
.agent-workflows/
  goals/
    .init.lock
    <slug>/
      brief.md
      goals.json
      ledger.jsonl
      .state.lock
      .pending-transaction.json  # transient; present only during recovery
```

- `<slug>` must be lowercase kebab-case and at most 64 characters.
- `goals/.init.lock` serializes descriptor-relative, no-overwrite plan publication.
- Initialization publishes a completed temporary plan with the platform's atomic no-replace directory primitive. If that primitive is unavailable, it stops without publishing state.
- `brief.md` is the stable human-readable objective and constraints.
- `goals.json` is the current plan projection and contains a monotonic `revision`.
- `ledger.jsonl` is an append-only logical audit trail. Every event contains the prior event hash.
- `.state.lock` serializes local mutations where the platform supports file locking.
- `.pending-transaction.json` makes an interrupted two-file mutation recoverable. The next locked command proves that it is the immediate successor of the current plan and ledger (or the identical already-written projection) before rolling it forward.
- Do not put mutable workflow state under `.codex/`, a skill installation directory, or a user-global directory.
- Do not create `.agent-workflows/` for a workflow that has no durable state.

The helper never edits `.gitignore`. Whether the target repository tracks these artifacts is a repository or user decision. Do not silently hide durable plan state from version control.

## Initialization input

Pass a UTF-8 JSON object to `init --spec`:

```json
{
  "objective": "Complete the migration without changing the public API.",
  "constraints": [
    "Preserve backward compatibility.",
    "Do not change production data directly."
  ],
  "verification": [
    "The focused migration tests pass.",
    "The full typecheck and build pass."
  ],
  "goals": [
    {
      "id": "G001",
      "title": "Lock the migration contract",
      "objective": "Add regression coverage for the current behavior.",
      "acceptance_criteria": [
        "The old and new representations are covered."
      ],
      "verification": [
        "Run the focused migration test command."
      ]
    }
  ]
}
```

All strings must be non-empty. Goal IDs must match `G` followed by at least three digits and must be unique. The helper preserves the declared order and initializes every goal as `pending`.

## Completion evidence

Pass this shape to `checkpoint --status complete --evidence-file`:

```json
{
  "summary": "The compatibility adapter and regression coverage are complete.",
  "artifacts": ["src/adapter.ts", "tests/adapter.test.ts"],
  "checks": [
    {
      "name": "focused tests",
      "status": "passed",
      "evidence": "12 tests passed"
    }
  ],
  "residual_risks": []
}
```

Completion requires at least one passing check, no failed check, and concrete artifacts or an explicit observation artifact. Use a repository-relative file, command output, screenshot, or named inspection result as evidence.

## Blocker evidence

Pass this shape to `checkpoint --status blocked --evidence-file`:

```json
{
  "summary": "The local fixture cannot reproduce the provider callback.",
  "blocker": "A credential-gated provider sandbox is required.",
  "attempts": ["Validated the local mock path", "Checked available test fixtures"],
  "needed_action": "Provide access to the provider sandbox or approve a recorded fixture."
}
```

A failing check, uncertainty, or slow progress is not automatically a blocker. Exhaust safe in-scope alternatives first.

## Final quality gate

Pass this shape to `finalize --quality-gate-file` after the native goal is complete:

```json
{
  "status": "passed",
  "implementation_changed": true,
  "requirements": [
    {
      "requirement": "Complete the migration without changing the public API.",
      "status": "proved",
      "evidence": "The final diff preserves the public API."
    },
    {
      "requirement": "Preserve backward compatibility.",
      "status": "proved",
      "evidence": "Compatibility tests passed against both representations."
    },
    {
      "requirement": "The old and new representations are covered.",
      "status": "proved",
      "evidence": "Regression cases exercise both representations."
    }
  ],
  "verification": [
    {
      "name": "The focused migration tests pass.",
      "status": "passed",
      "evidence": "The focused migration suite passed."
    },
    {
      "name": "The full typecheck and build pass.",
      "status": "passed",
      "evidence": "Typecheck and build exited successfully."
    },
    {
      "name": "Run the focused migration test command.",
      "status": "passed",
      "evidence": "The declared command passed."
    }
  ],
  "review": {
    "status": "passed",
    "evidence": "Independent read-only Codex review found no blocking issue."
  },
  "residual_risks": []
}
```

Use each durable requirement's exact text as its `requirement`: the plan objective, every constraint, and every acceptance criterion for completed goals. Use each declared global and completed-goal verification string as its exact verification `name`. The helper rejects missing or duplicate coverage.

Set `implementation_changed` to `true` when implementation artifacts changed; its review must then be `passed`. Set it to `false` for a non-implementation workflow and use review status `not_required` with a concrete explanation. Every listed requirement must be `proved` and every verification item must be `passed`.

Save the completed goal object returned by the successful `update_goal` call before making another goal query. A later `get_goal` may return no active goal after completion. The helper accepts either one direct goal object or one top-level `goal` object, rejects ambiguous nested candidates, and requires a `complete` goal whose objective matches either the original objective or the generated aggregate goal.

## Commands

Run every command with `--repo-root <repo>`. Mutations after initialization require the current revision from `status`. See [goal-state-cli.md](goal-state-cli.md) for output fields, exit behavior, recovery semantics, platform boundaries, and troubleshooting.

```text
goal_state.py --repo-root <repo> init --slug <slug> --spec <file>
goal_state.py --repo-root <repo> status --slug <slug>
goal_state.py --repo-root <repo> validate --slug <slug>
goal_state.py --repo-root <repo> start --slug <slug> --expected-revision <n> [--goal-id G001]
goal_state.py --repo-root <repo> checkpoint --slug <slug> --expected-revision <n> --goal-id G001 --status complete|blocked --evidence-file <file>
goal_state.py --repo-root <repo> resume --slug <slug> --expected-revision <n> --goal-id G001 --reason <text>
goal_state.py --repo-root <repo> append --slug <slug> --expected-revision <n> --goal-file <file> --reason <text>
goal_state.py --repo-root <repo> replace --slug <slug> --expected-revision <n> --goal-id G001 --goal-file <file> --reason <text>
goal_state.py --repo-root <repo> finalize --slug <slug> --expected-revision <n> --quality-gate-file <file> --goal-snapshot-file <file>
```

`append` and `replace` accept one goal object with the same fields as an initialization goal. Replacement is limited to `pending` or `blocked` work. The original entry remains `superseded`; history is never deleted.
