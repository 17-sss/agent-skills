# GitHub CLI PR Create Notes

Use this reference when maintaining the `github-pr-publish` command builder.

Official `gh pr create` behavior that shapes this skill:

- `gh pr create` creates a pull request and prints the URL on success.
- If the current branch is not fully pushed, the CLI can prompt where to push and can offer fork-based behavior.
- Supplying an explicit `--head` selects the PR head and avoids relying on implicit push/fork prompts.
- For same-repository PRs, pass the branch name to `gh pr create`. Do not pass an organization as the namespace in `OWNER:branch`; the CLI documents that organization namespaces are unsupported for this option.
- Supplying `--title` and `--body` or `--body-file` avoids title/body prompts.
- `--fill`, `--fill-first`, and `--fill-verbose` can derive content from commits; explicit title/body values take precedence.
- The CLI preview-style flag is not treated as safe by this skill because official documentation says it may still push git changes.

Skill policy:

- Validate the requested owner and remote against the target repository, then build an explicit branch-only `--head` argument for the same-repository CLI create path.
- Never rely on interactive prompts or editor flows.
- Preview mode is implemented by this package without calling the GitHub creation command.

## Remote forms and unverified SSH aliases

Supported GitHub remote forms include:

- `https://github.com/OWNER/REPO.git`
- `git@github.com:OWNER/REPO.git`
- `git@github.com-alias:OWNER/REPO.git` when `ssh -G github.com-alias` reports `hostname github.com`
- `ssh://git@github.com-alias/OWNER/REPO.git` with the same alias check

The trailing `.git` suffix is optional for these forms.

If an SSH alias cannot be verified as `github.com`, do not push through it. If `--head OWNER:branch` is explicit and no push is requested, the helper may still use the prompt-free create path after proving the local `HEAD` matches both the remote branch SHA and the GitHub branch SHA. The helper then passes `--head branch` to `gh pr create` because the head is in the verified target repository.


## Explicit-head no-push fallback

When the configured remote uses an SSH alias that the helper cannot safely treat as a GitHub remote, use this no-push fallback only for explicit heads:

```bash
remote_sha=$(git ls-remote origin "refs/heads/feature-branch" | awk 'NR==1{print $1}')
local_sha=$(git rev-parse HEAD)
test "$remote_sha" = "$local_sha"
gh pr create \
  --repo OWNER/REPO \
  --base main \
  --head feature-branch \
  --title "Add feature" \
  --body-file /tmp/pr-body.md
```

The bundled helper automates this fallback in execute mode by also checking the GitHub branch SHA before invoking `gh pr create`. If any SHA differs, stop and push or re-check the branch manually instead of creating the PR.
