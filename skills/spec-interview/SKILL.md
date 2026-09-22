---
name: spec-interview
description: Clarify ambiguous ideas or implementation requests through an evidence-grounded Socratic interview and produce an execution-ready requirements specification before planning or coding. Use when the user invokes $spec-interview, asks to be interviewed, says not to assume, or provides a broad request without clear scope, non-goals, decision boundaries, constraints, or testable completion criteria.
---

# Spec Interview

Recommended invocation: `Use $spec-interview to clarify <idea or task> before planning or implementation.` Use a read-only planning mode when the current agent provides one.

Remain in requirements mode. Do not implement the solution or modify project files while this skill is active.

## Ground the context

1. For repository work, inspect the applicable `AGENTS.md`, relevant documentation, current code, symbols, tests, and nearby patterns before asking questions.
2. Classify each uncertainty as one of:
   - a fact discoverable with tools
   - an interpretation that needs confirmation
   - a goal, boundary, preference, or tradeoff only the user can decide
3. Resolve discoverable facts with read-only tools. Cite concrete file paths, symbols, behavior, or authoritative external sources when they affect a question.
4. Inspect directly by default. For optional independent repository inspection, read [delegated-inspection.md](references/delegated-inspection.md) first; use it only behind a tool-enforced read-only boundary, then verify workspace integrity.

Do not ask the user for repository facts that can be established directly. If documentation and code disagree, present both pieces of evidence and ask which contract should govern.

## Interview one decision at a time

Maintain a working ledger for:

- goal and desired outcome
- in-scope behavior
- non-goals
- constraints
- decisions the agent may make autonomously
- decisions that require user approval
- testable completion conditions
- confirmed assumptions and unresolved risks

Ask the single highest-leverage unresolved question in each round.

- Apply the choice-presentation contract below whenever the question is a bounded decision.
- Use one concise plain-text question when the answer is genuinely open-ended.
- Wait for the answer before asking the next interview question.
- Prioritize intent, desired outcome, scope, non-goals, and decision boundaries before implementation detail.
- Pressure-test only material assumptions. Use one focused example, counterexample, terminology conflict, tradeoff, or boundary scenario.
- Stay on the same issue while another answer could materially change the implementation or its verification. Do not extend the interview to satisfy a round count or numeric score.

## Present bounded decisions as choices

Prefer the current agent's native structured-choice input when the evidence supports a small, complete option set.

- Ask exactly one decision per control, even if the interface accepts multiple questions.
- Provide 2 or 3 mutually exclusive options. Give each a short label and one concise sentence explaining its impact or tradeoff.
- Put the best-supported option first and mark it as recommended only when repository evidence or the user's stated priorities justify the recommendation.
- Preserve an `Other/custom` escape hatch. Do not duplicate it when the interface supplies one automatically.
- Do not force a closed choice when the option space is incomplete, options may be combined, terminology is unresolved, or the user's reasoning is itself required. Ask one open-ended question instead.
- Do not invent options merely to make a question look structured. Every option must be materially distinct and compatible with the evidence already gathered.

If native structured-choice input is unavailable, render the same decision as a numbered plain-text list with 2 or 3 options followed by `Other — answer in your own words.` Then wait for one selection or custom answer. Keep the fallback visually scannable:

```text
Which compatibility policy should govern existing clients?

1. Preserve all clients (Recommended) — safest rollout, but it keeps the legacy path longer.
2. Set a version cutoff — simpler implementation, but older clients must upgrade.
Other — answer in your own words.
```

## Apply the readiness gate

End ordinary questioning when all of the following are true:

- the desired outcome is concrete
- in-scope and out-of-scope behavior are explicit
- material constraints are known
- the agent's decision boundary is explicit
- completion can be tested or observed
- another answer would not materially change the implementation direction or acceptance decision

If the user ends early, preserve the remaining ambiguity and its likely consequence instead of presenting the brief as fully resolved.

## Crystallize the specification

Return an execution-ready specification with:

1. Goal
2. Desired outcome
3. In scope
4. Non-goals
5. Constraints
6. Decision boundaries
7. Testable acceptance criteria
8. Confirmed assumptions
9. Repository or external evidence
10. Remaining decisions and residual risks

Do not begin implementation. Hand the specification to the planning or execution workflow selected by the user. Save it to the repository only when the user explicitly requests a durable artifact and the repository provides an appropriate path.

## Offer an optional next workflow

After the readiness gate passes, offer at most one best-fit workflow and one genuinely applicable alternative. Skip this section if the user ends early, a material decision or authority is missing, or the user asks to stop. Keep this package complete: never invoke, install, or automatically start a downstream skill.

Check the exact name in the current task's available-skill inventory and its advertised runtime requirements. Do not inspect installation directories, catalog files, or downstream contents to infer availability. If the inventory is unavailable or compatibility is unclear, make no suggestion. The user must explicitly choose and invoke a suggested workflow later.

| Accepted work | Best-fit suggestion |
| --- | --- |
| Architecture, security, migration, destructive, public-contract, or compliance risk | `$reviewed-plan` |
| Ordered, independently verifiable, restartable stages | `$milestone-runner` |
| One scoped implementation goal with acceptance and verification criteria | `$completion-loop` |

Do not substitute a weaker route merely because the best fit is unavailable. A missing `$reviewed-plan` yields no suggestion. If `$milestone-runner` is unavailable, suggest `$completion-loop` only when the accepted scope can be executed safely as one goal. Render any suggestion as a copyable invocation and stop before planning or implementation.
