---
name: commit-helper
description: Inspect explicit repo-local commit rules, recent history, and staged changes to draft commit messages in the right style family. Use when the user asks for a commit message, asks to commit staged changes, or wants help choosing between conventional, gitmoji, plain imperative, or repo-custom commit formats.
---

# Commit Helper

Draft or create staged-only commits that match the target repository. Supported style families are Conventional Commits, gitmoji/emoji, plain imperative, and repo-custom rules.

## Invocation Boundary

When this skill is invoked, commit-message construction is governed by **commit-helper only**:

- Use only explicit repo-local rules, recent history, staged diff semantics, and direct user wording preferences.
- Do not add external harness metadata, Lore trailers, hidden workflow notes, automation attribution, or co-author trailers unless the repository's committed rules/templates or the user explicitly require them.
- Prefer `scripts/draft_commit_message.py ... --commit` over raw `git commit -m ...` so the staged-only title/body contract cannot be changed by an external inline-message layer.
- If a hook demands non-repo trailers or automation attribution, report the blocker. Do not use `--no-verify` unless the user explicitly asks.

## Workflow

1. Identify the target repository and read its `AGENTS.md` instructions.
2. Use `scripts/draft_commit_message.py <repo-path> --summary ...` as the single standard path. It runs the canonical repository inspection internally; do not run `inspect_commit_style.py` first.
3. When the user already authorized the commit, add `--commit` to that same invocation. Do not draft once and rerun solely to commit unless the result is genuinely ambiguous or needs user review.
4. Use `inspect_commit_style.py` directly only when the user asks for inspection/diagnosis without a draft, or when debugging the helper itself.
5. Review the returned title, warnings, and commit status. Report failures without retrying through a different message path.

`--summary` accepts either subject text or an already formatted Conventional Commit title. The script extracts existing type/scope prefixes before formatting so it does not produce titles such as `docs: fix: ...`. Explicit `--type` and `--scope` options override values parsed from the summary.

## Essential Rules

- Draft from staged changes only and keep unrelated unstaged work out of the title.
- Apply evidence in this order: explicit repo-local rules, recent history, conservative fallback.
- Treat format and phrasing separately. Infer meaning from the staged diff and user summary, then express it in the repository's preferred style and language.
- Use Conventional Commits only as the fallback when stronger local evidence is absent.
- Activate gitmoji only from repo-local config/docs or clearly emoji-dominant history, and obey any local allowlist.
- Keep bugfix classification conservative; layout, spacing, wrapper cleanup, and similar presentation changes are not bugfixes by default.
- Prefer title-only commits unless local rules/history require a body. Pass repeated `--body-line` values for a body; never place a literal `\n` in it.
- Use path-derived scopes as weak hints. Explicit user wording and staged-diff intent are stronger.

For detailed semantic categories, phrasing guidance, and style-family policy, read [references/commit-patterns.md](references/commit-patterns.md) only when the ordinary script output is insufficient.

## Commands

Draft a title-only message:

```bash
python3 scripts/draft_commit_message.py <repo-path> --summary "..." --no-body
```

For an authorized commit, add `--commit` to the draft command. For a multiline body, pass repeated `--body-line` values:

```bash
python3 scripts/draft_commit_message.py <repo-path> --summary "..." --body-line "first bullet" --body-line "second bullet" --commit
```

## Resources

- `scripts/draft_commit_message.py`: standard draft and commit path; performs repository inspection once.
- `scripts/inspect_commit_style.py`: standalone inspection and diagnostic output.
- `scripts/run_behavior_evals.py`: deterministic behavioral regression checks.
- `references/commit-patterns.md`: detailed style and fallback policy.
- `evals/behavior_cases.json`: behavioral evaluation inventory.
