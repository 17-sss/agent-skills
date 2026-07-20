# Review Gate Contract

Use this contract to keep two independent review lanes comparable and to prevent missing evidence from becoming approval.

## Priority

| Priority | Meaning | Default merge effect |
| --- | --- | --- |
| `P0` | Active exploit, data loss, or broadly catastrophic failure | Blocking |
| `P1` | Likely correctness, security, authorization, compatibility, or operational failure in normal use | Blocking |
| `P2` | Real but narrower defect, regression risk, or important test gap | Context-dependent |
| `P3` | Small maintainability or robustness issue with concrete future cost | Non-blocking |

Priority describes impact and urgency. Set `merge-blocking` separately because a narrow but release-critical `P2` can block while a migration follow-up may not.

## Finding acceptance

Accept a finding only when all of these are present:

- for a change review, the selected change introduces or materially exposes it; for a file audit, the defect exists in the captured selected-file content
- a concrete code path, input, state, or failure scenario triggers it
- the cited line range is tight enough to act on
- the impact is more than a generic preference
- the proposed direction addresses the cause rather than only the symptom

If evidence is incomplete, omit the finding or label it as a validation gap. Do not inflate confidence by repeating the same concern from both lanes.

## Lane statuses

Correctness lane:

- `APPROVE` — no actionable correctness-lane finding remains
- `COMMENT` — only non-blocking findings remain
- `REQUEST_CHANGES` — at least one blocking correctness finding remains

Architecture lane:

- `CLEAR` — no actionable architecture concern remains
- `WATCH` — a non-blocking tradeoff or follow-up must remain visible
- `BLOCK` — an unresolved design concern prevents merge readiness

## Final verdict precedence

Apply the first matching rule:

1. `INCONCLUSIVE` — the scope is unreadable or drifted, a required read-only isolation gate is unavailable, a lane packet digest changed, the applicable worktree or selected-file baseline changed during review, or either required independent lane is missing, failed, or evidence-free.
2. `REQUEST_CHANGES` — any accepted finding is merge-blocking, correctness is `REQUEST_CHANGES`, or architecture is `BLOCK`.
3. `COMMENT` — correctness is `COMMENT`, architecture is `WATCH`, or non-blocking findings remain.
4. `APPROVE` — both lanes completed with evidence, correctness is `APPROVE`, architecture is `CLEAR`, and no accepted finding remains.

Operational unavailability is `INCONCLUSIVE`, not `REQUEST_CHANGES`: both prevent approval, but only the latter asserts a defect in the code.

## Compact output shape

```text
Findings
- [P1] Short actionable title — path/to/file:line
  Evidence: ...
  Impact: ...
  Fix direction: ...
  Merge-blocking: yes

Architecture watchlist
- ...

Synthesis
- Correctness: APPROVE | COMMENT | REQUEST_CHANGES
- Architecture: CLEAR | WATCH | BLOCK
- Final: APPROVE | COMMENT | REQUEST_CHANGES | INCONCLUSIVE

Scope and evidence
- Reviewed: ...
- Checks: ...
- Gaps: ...
```
