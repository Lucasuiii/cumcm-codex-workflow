# Architecture

v0.5 stores durable state in workspace files but separates orchestration from work products.

```text
orchestrator
  -> modeling artifacts
  -> modeling-computation handoff
  -> one selected computation backend + official run
  -> computation-validation handoff + review package
  -> bounded validation
  -> validation-paper handoff
  -> fresh paper task
  -> paper-delivery handoff
  -> compile receipt and three-part delivery
```

The top-level state machine remains seven stages for compatibility, while responsibilities are grouped into orchestrator, modeling, computation, validation, paper, and delivery. Independent review stays a validation gate; it is not another self-approved stage.

`working` and `finalizing` control gate intensity. Working mode preserves the hard evidence chain without requiring downstream completeness. Finalizing mode requires passed state, decisions, snapshots, handoffs, review, and exact final bindings.

Accepted decision scopes are the canonical source for stage snapshots. Handoffs reuse the same small set of stage artifacts and compute an upstream digest. This avoids a second manual maintenance schema. The review package is the exception that copies files because the reviewer may operate in another task or workspace.

`workflow_checks.py` always rechecks cheap hard invariants. Trusted snapshots suppress the need for repeated human/semantic review; they do not suppress official-source, run, result, review-package, handoff, or final-PDF identity checks.

Official computation binds one selected MATLAB/Python implementation to a source-tree snapshot, successful command, inputs, outputs, logs, assertions, and results. Final compilation similarly binds the PDF to the editable LaTeX source-tree snapshot.
