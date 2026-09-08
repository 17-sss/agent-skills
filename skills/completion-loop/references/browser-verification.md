# Browser Verification

Read this only when the frozen contract requires browser interaction or rendered evidence. Use the existing evidence ledger for every result, capture, failure classification, and resource owner.

## Bound coverage before running

Reuse the repository's runner, browser setup, and deterministic fixtures first. Fix seeds, data, routes, and state-entry controls where already supported. Do not introduce another runner or require another skill just to orchestrate the same checks.

Define two sets in the ledger before capture:

- **Development representatives:** the smallest useful cases covering the changing behavior and plausible regression boundaries.
- **Final required coverage:** the combinations required by the approved plan, acceptance criteria, risk tier, and any explicitly invoked visual workflow.

Do not automatically multiply every screen, appearance/theme, time point, and environment into a Cartesian product. Select representatives by risk and behavior; a shared renderer or host change may require expanding them. Explicitly required combinations are never samples to discard. Preserve the specified visual-review count and consecutive-pass condition: a requirement for three visual reviews still needs three actual reviews. Reusing a valid artifact is allowed only when the contract permits it; one old review cannot satisfy a new review or stability sequence.

## Keep the served candidate stable

Before a run, record the server owner, URL/base path, build identity, fixture, renderer, environment, and bounded readiness condition. Verify the actual route and required assets respond and the app reaches the intended state. A listening port alone does not prove readiness. Wait on observed conditions within a deadline instead of blind sleeps; report a readiness failure when the deadline expires.

Do not rebuild static output while a verification server is serving it to active checks. Finish or stop the captures/checks first, stop the task-owned server or isolate the next build in a separate directory, and start a new run pinned to one complete build. Never point an active run at files being replaced. Invalidate evidence affected by any build change.

Readiness waits must not weaken product timing requirements. If the requirement is visible feedback within 500 ms, animation duration, or an event at a specified time, retain its clock origin, deadline, and sampling condition. Moving the timer start until after readiness, lengthening the bound, or replacing a timed assertion with an eventual-success wait changes the requirement.

## Diagnose before retrying

Capture the first decisive error and inspect the runner command, URL, HTTP response, console/network output, fixture state, and build identity as relevant. Classify with evidence before modifying code:

| Failure class | Evidence and response |
| --- | --- |
| Product defect | Correct route, build, fixture, and supported environment reproduce a contract violation; repair the product and recheck affected behavior |
| Test or fixture error | The runner uses an incorrect base path, stale asset, invalid seed/state, or unsupported expectation; correct it against the approved requirement and invalidate its dependent results |
| Execution-environment error | Missing browser/device, crashed server, unavailable service, or resource contention prevents the observation; restore only authorized task resources or report missing evidence |

A browser `404` alone does not identify the class. Check the requested URL and base path, response, built asset existence, and serving process/build before deciding. A valid product route missing from the correct build may be a product defect; a runner navigating the wrong prefix may be a test error. Do not immediately rebuild everything, change an expected status to `404`, or repeat the same navigation without a diagnosis.

Change an expectation only with independent evidence from the approved behavior or a reproducible fixture error. Preserve the reason in the ledger and rerun invalidated observations. After an unchanged failure recurs, stop that retry strategy and inspect its cause. A flaky run is not a pass; preserve any required consecutive-pass sequence.

## Release task resources

Track task-owned browser sessions/contexts, servers, workers, and child process groups when starting them. Reuse existing shared services without assuming ownership. On completion, failure, or interruption, close owned sessions and stop owned processes in dependency order using the runner's cleanup or a `finally` path.

Confirm actual release: owned processes and descendants exited, owned listening ports were released, and browser sessions/workers are closed. A cleanup command returning zero is not sufficient if children remain. Retry cleanup only for identified task resources and report any residue; never kill shared or user-owned sessions to make the check green. Retain required original logs/captures even when temporary runtime resources are removed.
