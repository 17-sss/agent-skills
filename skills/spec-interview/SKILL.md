---
name: spec-interview
description: Clarify ambiguous ideas or implementation requests through an evidence-grounded Socratic interview and produce an execution-ready requirements specification before planning or coding. Use when the user invokes $spec-interview, asks to be interviewed, says not to assume, or provides a broad request without clear scope, non-goals, decision boundaries, constraints, or testable completion criteria.
---

# Spec Interview

Recommended invocation: `/plan $spec-interview <idea or task>`.

Remain in requirements mode. Do not implement the solution or modify project files while this skill is active.

## Ground the context

1. For repository work, inspect the applicable `AGENTS.md`, relevant documentation, current code, symbols, tests, and nearby patterns before asking questions.
2. Classify each uncertainty as one of:
   - a fact discoverable with tools
   - an interpretation that needs confirmation
   - a goal, boundary, preference, or tradeoff only the user can decide
3. Resolve discoverable facts with read-only tools. Cite concrete file paths, symbols, behavior, or authoritative external sources when they affect a question.
4. Use a subagent only when an independent repository map materially improves speed or confidence. Keep human decisions with the main agent.

Before delegated repository inspection, prove that the reviewer runs under a tool-enforced Codex `read-only` sandbox. A prose instruction to remain read-only is not enforcement because native subagents inherit the parent permission mode. Use an inherited read-only parent turn or another native isolated Codex run whose effective sandbox is explicitly read-only. Keep the inspection lane bounded: it must not activate another workflow or delegate recursively. If isolation cannot be proved, skip optional delegation and inspect directly in the main context.

Also capture a content fingerprint from the current `HEAD`, staged and unstaged diff bytes, and a canonical serialization of each untracked path's file type, executable mode bits, symlink target when applicable, and content or content hash. Compare it after the subagent returns as defense in depth. If the fingerprint changed, stop the interview, report the exact drift, preserve the files, and do not trust the delegated result.

Do not ask the user for repository facts that can be established directly. If documentation and code disagree, present both pieces of evidence and ask which contract should govern.

## Interview one decision at a time

Maintain a working ledger for:

- goal and desired outcome
- in-scope behavior
- non-goals
- constraints
- decisions Codex may make autonomously
- decisions that require user approval
- testable completion conditions
- confirmed assumptions and unresolved risks

Ask the single highest-leverage unresolved question in each round.

- Use native structured input in Plan mode when it faithfully represents a bounded decision.
- Use one concise plain-text question when the answer is open-ended or structured input is unavailable.
- Wait for the answer before asking the next interview question.
- Prioritize intent, desired outcome, scope, non-goals, and decision boundaries before implementation detail.
- Pressure-test only material assumptions. Use one focused example, counterexample, terminology conflict, tradeoff, or boundary scenario.
- Stay on the same issue while another answer could materially change the implementation or its verification. Do not extend the interview to satisfy a round count or numeric score.

## Apply the readiness gate

End ordinary questioning when all of the following are true:

- the desired outcome is concrete
- in-scope and out-of-scope behavior are explicit
- material constraints are known
- Codex's decision boundary is explicit
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
