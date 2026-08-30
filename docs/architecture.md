# Architecture

The project uses files as the durable workflow state.

```text
official sources
  -> source manifest and problem facts
  -> task capabilities and model contract
  -> executable code and immutable run directory
  -> exact result index
  -> validation report, claim ledger, and figure manifest
  -> paper plan and claims-evidence matrix
  -> versioned paper, content review, rendered-page review, revision log
  -> compile receipt and delivery manifest
```

The Codex skill routes the active stage. `cumcm_check.py` validates local JSON Schemas and crosses stable IDs between artifacts. It records typed findings for structural, execution, numerical, semantic, and visual evidence. `record_decision.py` appends approvals bound to the current stage-owned bytes, so later edits invalidate the old approval without deleting its history. Human review controls interpretation, model choice, claim scope, paper quality, and submission. Mathematical correctness remains an evidence question rather than a workflow-status flag.

Version 0.3 is the only accepted contract version. The top-level seven-stage state machine stays small; paper and delivery gain stage-owned subcontracts without adding routing stages. The paper scaffold is generated from problem facts and the paper plan, while the validator checks its file inventory, per-question coverage, placeholders, compile engine, and official-format review status.
