# Goal state CLI reference

Use `scripts/goal_state.py` to manage only the durable repository artifacts for `milestone-runner`. The helper does not call native Codex goal tools, edit implementation files, change `.gitignore`, install dependencies, or invoke another skill.

Read [state-contract.md](state-contract.md) for every JSON input schema and finalization requirement.

## Runtime boundary

- Pass an existing target directory through `--repo-root`; the helper resolves it before accessing state.
- New-plan publication currently targets Linux and macOS POSIX hosts with an atomic no-replace directory primitive. Initialization stops before publishing state when that primitive is unavailable.
- Keep one writer per plan. File locks serialize cooperating local processes, while `--expected-revision` rejects stale mutations.
- Treat `.agent-workflows/` as project data. The helper never decides whether to commit or ignore it.

## Exit and output contract

- Success exits `0` and prints one JSON object to standard output.
- Invalid input, an illegal transition, a stale revision, unsafe path state, or failed reconciliation exits `2` and prints an `ERROR:` message to standard error.
- An unexpected interpreter or operating-system failure returns a nonzero exit and must not be treated as a valid checkpoint.
- `status` and `validate` are normally observational. If a prior mutation stopped after writing a complete pending transaction, the next locked command may atomically roll that exact immediate successor forward before returning.

The common success fields are:

| Field | Meaning |
| --- | --- |
| `path` | Absolute plan directory |
| `slug` | Durable plan identifier |
| `status` | `active`, `blocked`, or `complete` |
| `revision` | Monotonic value required by the next mutation |
| `aggregate_goal` | Exact objective to use with native Goal mode |
| `current_goal` | First non-terminal goal, or `null` |
| `ready_to_finalize` | All local goals are terminal but the plan is not finalized |

`validate` returns `valid`, `path`, `revision`, and `ledger_events` instead of the normal status projection.

## Command lifecycle

Run the helper through its installed package path:

```text
python3 <skill-dir>/scripts/goal_state.py --repo-root <repo> <command> ...
```

| Command | Mutation | Contract |
| --- | --- | --- |
| `init` | Yes | Create a new plan from `--spec`; refuse an existing slug |
| `status` | Recovery only | Return the current revision and first eligible goal |
| `validate` | Recovery only | Verify schema, slug binding, ledger chain, projection hash, brief, and pending transaction |
| `start` | Yes | Start only the first non-terminal goal |
| `checkpoint` | Yes | Mark an in-progress goal `complete` or `blocked` with evidence |
| `resume` | Yes | Resume the first blocked goal after its blocker changes |
| `append` | Yes | Append a new evidence-backed pending goal |
| `replace` | Yes | Supersede pending or blocked work while preserving history |
| `finalize` | Yes | Reconcile the quality gate with a completed native goal result |

Every mutation after `init` requires the revision returned by a fresh `status` call:

```text
python3 <skill-dir>/scripts/goal_state.py --repo-root <repo> status --slug <slug>
python3 <skill-dir>/scripts/goal_state.py --repo-root <repo> start --slug <slug> --expected-revision <revision>
```

Do not reuse a revision after any successful mutation. Run `status` again and use the new value.

## Input files

The CLI accepts UTF-8 JSON files:

| Option | Used by | Schema |
| --- | --- | --- |
| `--spec` | `init` | Objective, constraints, global verification, and ordered goals |
| `--evidence-file` | `checkpoint` | Completion evidence or blocker evidence matching `--status` |
| `--goal-file` | `append`, `replace` | One new goal object with a unique ID |
| `--quality-gate-file` | `finalize` | Complete requirement and verification coverage plus conditional review |
| `--goal-snapshot-file` | `finalize` | Completed goal object saved from the successful native `update_goal` result |

The helper reads these inputs but never rewrites them.

## Recovery and integrity

- Each event links to the prior ledger hash and records the resulting plan projection hash.
- Each mutation first writes `.pending-transaction.json`, then publishes the ledger and plan with atomic file replacement.
- Recovery accepts only the immediate successor of the current projection or the identical already-published result. It rejects stale transactions instead of rolling state backward.
- Descriptor-relative, no-follow access prevents state paths from escaping through symlink substitution.
- Do not manually edit `brief.md`, `goals.json`, `ledger.jsonl`, lock files, or a pending transaction. Use `append`, `replace`, `resume`, and `checkpoint` for supported changes.

## Common failures

| Error fragment | Action |
| --- | --- |
| `plan already exists` | Choose the existing plan intentionally or use a different slug; initialization never overwrites |
| `revision mismatch` | Run `status`, inspect the newer state, and retry with its revision |
| `next eligible goal is ...` | Complete, resume, or replace the earlier goal first |
| `does not extend the current plan` | Preserve the files and inspect the stale pending transaction; do not force recovery |
| `projection hash` or `hash chain` | Stop mutations and inspect unexpected manual edits or file corruption |
| `atomic no-replace ... unavailable` | Run initialization on a supported host; the helper has not published the new plan |

The helper intentionally has no delete command. Removing durable state requires a separate, explicit repository decision after the result and recovery needs have been reviewed.
