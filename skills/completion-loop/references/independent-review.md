# Completion Loop Independent Review

Read this only when the frozen risk tier or user requires independent review.

Run each required lane in tool-enforced read-only execution. Keep it terminal and prevent recursive delegation; if isolation is unavailable, leave the gate pending.

## Frozen independent-review packet

Every independent lane receives the same content-pinned packet:

- exact `base...HEAD` range, plus a canonical staged, unstaged, and untracked overlay when the candidate is not fully committed;
- one deterministic packet digest;
- objective, requirements, and acceptance criteria;
- non-goals;
- actual deployment target;
- risk tier and required evidence;
- valid verification evidence with input identities and paths to necessary original logs; and
- known existing failures and unavailable environments.

Do not give a reviewer the desired verdict or leader diagnosis. Require reproducible blockers, coverage gaps, deferred observations, residual risks, and confidence. Include this exact boundary:

> Do not invent requirements. Findings outside the frozen completion contract must be reported as deferred observations, not blockers.

Correctness and architecture lanes may be separate, but both must use the same packet and digest. Recompute the candidate fingerprint after review. Adopt a finding only after reproducing it in the actual code and mapping it to the frozen blocker definition.

## Review budget and focused rereview

- Spend at most one initial full-scope review on the first candidate.
- After an accepted blocker is fixed, review only its cause, modified files, directly connected call path, new regression tests, and plausible adjacent regressions.
- Do not rescan the already-passed codebase or seek another verdict on the same packet.
- Allow one additional full-scope review only for a recorded core-architecture change. If that change is outside the frozen contract, obtain expansion approval first.
- Spend at most one final full verification as the initial stable-candidate run after focused checks and review blockers are clear. Later runs cover failed or invalidated entries; broad or uncertain invalidation may require the full suite. Required repetitions are not redundant runs.

During focused rereview, keep a regression introduced by the current fix as a blocker. Keep a pre-existing issue as a blocker only when it fails an acceptance criterion. Defer findings outside the frozen contract. Escalate ambiguous classification to the user instead of expanding automatically.
