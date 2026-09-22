# Manual GitHub PR Collection

Use only when the bundled collector is unavailable or cannot cover the requested read-only context. Sanitize command output before writing artifacts.

Or collect manually:

```bash
gh pr view <pr> --json title,body,author,labels,baseRefName,headRefName,headRefOid,additions,deletions,changedFiles,files,reviews,reviewRequests,statusCheckRollup
gh pr diff <pr> --name-only
gh pr diff <pr>
gh pr checks <pr>
```
