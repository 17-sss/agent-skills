# GitHub REST Create Pull Request Notes

Use this reference when maintaining REST fallback behavior.

Official REST requirements for creating a pull request:

- Endpoint: `POST /repos/{owner}/{repo}/pulls`.
- Fine-grained tokens need Pull requests repository permission with write access.
- Required body fields include `head` and `base`.
- `title` is required unless converting an existing issue.
- Cross-repository PR heads are namespaced like `username:branch`.
- A successful create response is HTTP `201` and includes the pull request URL fields.
- Private repositories can return forbidden or not-found style failures when credentials lack access or organization SSO is not authorized.

Skill policy:

- REST fallback is allowed only after repository verification and remote-head proof.
- Do not infer repository visibility from clone URLs.
- Classify SSO, authentication, permission, private not-found masking, and validation failures separately when possible.

## Invoking the fallback

### 7. REST fallback

Use REST only when the remote head already exists and the CLI create path is blocked:

```bash
skills/github-pr-publish/scripts/create_pr.sh \
  --repo OWNER/REPO \
  --base main \
  --head OWNER:feature-branch \
  --title "Add feature" \
  --body-file /tmp/pr-body.md \
  --use-rest \
  --yes
```

REST creation requires `head`, `base`, and `title` unless converting an issue. Success must return HTTP `201` and a PR URL.
