---
name: minimal
description: Find and implement the smallest correct change within accepted scope. Use $minimal only when the user explicitly asks to prioritize reuse and platform capabilities over unnecessary code, abstractions, files, configuration, or dependencies.
---

# Minimal

## Purpose and boundary

Use this explicit-only, cross-agent skill to choose the smallest **correct** implementation for accepted behavior. Minimize implementation complexity, not the user's requirements: minimal does not mean fewest lines, code golf, skipped requirements, or skipped verification.

This is an implementation-strategy skill, not an execution, planning, review, or task-orchestration workflow. Keep this package standalone: do not search for, install, require, or invoke another skill.

Use one meaning only: do not add a persona or intensity modes. Do not register always-on lifecycle callbacks, inject persistent behavior, or create global state; apply this strategy only to the explicitly invoked current task.

When another explicitly active workflow defines authority, scope, acceptance criteria, evidence, verification, or review, that workflow owns those contracts. `$minimal` governs only the implementation choice within them; it must not weaken or remove their gates.

## Understand the real change first

Before selecting a solution, establish the requested behavior and its accepted scope. Inspect, in proportion to risk:

- the actual execution and data flow;
- relevant callers, callees, shared helpers, and existing patterns;
- repository conventions and existing tests; and
- affected trust, compatibility, migration, and error-handling boundaries.

Do not pick an apparently small file-local patch before understanding the affected flow. If the requested outcome already works, demonstrate that with appropriate evidence and avoid an unnecessary code change; do not use YAGNI to reject behavior the user has explicitly requested.

For a bug, prefer the smallest root-cause fix over a symptom patch. A shared correction can be smaller and safer when several callers have the same defect, while a local correction is preferable when broadening the affected surface would be unnecessary or unsafe. Judge minimality by correctness and affected surface, not lines changed.

## Choose the smallest coherent solution

After understanding the change, stop at the first reliable option that satisfies the accepted behavior:

1. Reuse existing project code or an established local pattern.
2. Use the language standard library.
3. Use a native platform capability.
4. Use an already-installed dependency when it solves the need cleanly.
5. Add the smallest coherent implementation that remains.

Avoid speculative abstractions and infrastructure: a single implementation does not automatically need an interface, factory, wrapper, utility, configuration layer, feature flag, plugin system, new file, build step, service, or dependency. Do not force unrelated responsibilities into one file merely to reduce file count. An abstraction is appropriate when the current accepted behavior actually requires multiple implementations, runtimes, or a public extension contract.

Add a new dependency only when existing project code, the standard library, native capabilities, and installed dependencies cannot meet the requested behavior, and its cost is justified by the current requirement. Do not install packages or configure systems merely to explore a hypothetical option.

## Use discovery capabilities without depending on them

When the current runtime provides Graft retrieval, graph, or blast-radius capabilities, use them when they are the cheapest reliable way to locate relevant code, inspect an API shape, trace callers, or assess impact. When unavailable, use ordinary repository search and source reading. Treat any graph or summary as discovery assistance, then confirm decision-critical facts in source and executable evidence. Never install or configure Graft from this skill.

## Preserve non-negotiable behavior

Never simplify away explicit user requirements, security controls, authorization checks, trust-boundary validation, data-loss prevention, required error handling, accessibility, compatibility, migration safety, repository-mandated checks, or tests needed to demonstrate changed behavior.

After editing, run the smallest decisive verification justified by the changed behavior, repository convention, actual risk, and any active workflow contract. Reuse relevant existing tests and add focused regression evidence when appropriate. Do not create a new test framework, oversized fixture, full integration suite, or browser harness unless the current requirement needs it.

Skill invocation does not authorize dependency or system installation, commits, pushes, pull requests, deployment, external mutations, paid API use, credentials, or destructive operations.

## Report the decision

Briefly state the accepted behavior, the reuse or implementation choice, the decisive verification, and any unverified boundary. Do not impose a terse response style when the user asks for explanation or a report.
