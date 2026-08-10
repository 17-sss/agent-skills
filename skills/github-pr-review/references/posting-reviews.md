# Posting GitHub Reviews

Read this reference only after the user explicitly asks to publish a review or confirms a prepared draft. Keep review drafting read-only until then.

## Post a Summary Review

For a normal comment review:

```bash
gh pr review <pr> --comment --body-file review.md
```

The bundled helper wraps this path:

```bash
skills/github-pr-review/scripts/post_review.sh <pr> review.md
```

Only use these events when the user explicitly requests them:

```bash
gh pr review <pr> --approve --body-file review.md
gh pr review <pr> --request-changes --body-file review.md
```

Summary reviews must follow the PR Scope Rule in `SKILL.md`. Do not use a summary review to publish findings anchored outside the PR diff or to bypass inline diff-line requirements. Keep a finding internal or omit it when no reliable diff anchor exists.

## Verify Inline Line Mapping

Inline comments must point to lines present in the PR diff, not merely to a line in the base branch. For new or modified code, use `side: RIGHT` and the target line number from the PR's head-side file. Use `side: LEFT` only for removed lines.

Prefer an inline comment when a finding maps reliably to a changed diff line or range. Use a summary finding only when the PR Scope Rule still holds and inline mapping is uncertain.

Before posting inline comments:

1. Inspect the patch:

   ```bash
   gh pr diff <pr>
   ```

2. Confirm the local file line when a checkout is available:

   ```bash
   nl -ba path/to/file.ext | sed -n '120,140p'
   ```

3. Confirm the file's PR patch when possible:

   ```bash
   gh api repos/OWNER/REPO/pulls/NUMBER/files --paginate \
     --jq '.[] | select(.filename == "path/to/file.ext") | .patch'
   ```

4. Verify that the target is an added or context line in a diff hunk for `side: RIGHT`.
5. If mapping remains uncertain, do not post inline comments. Use a summary only with a reliable PR diff anchor; otherwise keep the finding internal or omit it.

REST review comments use `line` and `side`, plus optional `start_line` and `start_side` for a verified range. Avoid deprecated `position` mapping unless the environment requires it. GraphQL is appropriate for review-thread operations such as threads or replies. An installed `gh pr-review` extension is optional; the workflow must work with plain `gh pr review` and `gh api`.

## Post Inline Review Comments

Prefer one review payload and `gh api --input` for one or more inline comments. This avoids fragile shell-expanded nested `comments[]` flags.

Create a task-scoped temporary JSON payload. Use a sanitized repository slug and PR number, such as `/tmp/owner-repo-pr123-review.json`. Never include tokens, secrets, raw authorization headers, or unrelated private logs.

```json
{
  "event": "COMMENT",
  "body": "Reviewed the diff and left inline comments.",
  "comments": [
    {
      "path": "src/example.ts",
      "line": 42,
      "side": "RIGHT",
      "body": "This condition now allows an empty value through. Please add a guard or a regression test for that case."
    },
    {
      "path": "src/other.ts",
      "line": 87,
      "side": "RIGHT",
      "body": "This call can now run before the token is initialized. Consider keeping the previous ordering or handling the missing-token branch."
    }
  ]
}
```

Post the payload:

```bash
gh api repos/OWNER/REPO/pulls/NUMBER/reviews \
  --method POST \
  --input /tmp/owner-repo-pr123-review.json \
  --jq '{id, state, html_url}'
```

The expected state for a comment-only review is `COMMENTED`. Give the returned `html_url` to the user. Delete the exact task-scoped payload after posting when it is no longer needed:

```bash
rm /tmp/owner-repo-pr123-review.json
```

Only set `"event": "APPROVE"` or `"event": "REQUEST_CHANGES"` when the user explicitly asked for that action. For multi-line comments, add `start_line` and `start_side` only after verifying both ends of the range.

## Verify the Posted Review

Verify the create response and, when useful, confirm it through the review list:

```bash
review_id=123456789
gh api repos/OWNER/REPO/pulls/NUMBER/reviews --paginate \
  --jq ".[] | select(.id == $review_id) | {id, state, html_url, user: .user.login}"
```

Confirm that:

- `state` is `COMMENTED` for a normal comment review.
- `html_url` is present and points to the submitted review.
- `user.login` matches the authenticated account.
- The user receives the `html_url` or a concise statement of where the review was posted.

## Posting Failures

- If `gh pr review` cannot express the required inline comments, use `gh api` with REST or GraphQL.
- If GitHub returns a validation error, re-check `path`, `line`, `side`, range endpoints, and whether the target line is present in the diff.
- Fall back to a summary review only when the finding still has a reliable PR diff anchor; otherwise omit it from the posted review.
- Mention browser automation only as a last fallback when CLI/API access is blocked and the user explicitly wants to proceed that way.
