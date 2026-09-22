# Optional Delegated Inspection

Read only when independent repository inspection would materially improve the interview.

Use a delegated worker only when an independent repository map materially improves speed or confidence. Keep human decisions with the main agent.

Before delegated repository inspection, prove that the worker runs behind a tool-enforced `read-only` boundary. A prose instruction to remain read-only is not enforcement. Use delegation only when the current agent can prove the delegated execution cannot write to the repository or external systems. Keep the inspection lane bounded: it must not activate another workflow or delegate recursively. If isolation cannot be proved, skip optional delegation and inspect directly in the main context.

Also capture a content fingerprint from the current `HEAD`, staged and unstaged diff bytes, and a canonical serialization of each untracked path's file type, executable mode bits, symlink target when applicable, and content or content hash. Compare it after the subagent returns as defense in depth. If the fingerprint changed, stop the interview, report the exact drift, preserve the files, and do not trust the delegated result.
