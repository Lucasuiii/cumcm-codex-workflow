# Architecture

The project uses files as the durable workflow state.

```text
official sources
  -> source manifest and problem facts
  -> task capabilities and model contract
  -> executable code and immutable run directory
  -> exact result index
  -> validation report, claim ledger, and figure manifest
  -> LaTeX paper
  -> delivery manifest
```

The Codex skill routes the active stage. `cumcm_check.py` validates local JSON Schemas and crosses stable IDs between artifacts. It records typed findings for structural, execution, numerical, semantic, and visual evidence. Human review controls interpretation, model choice, claim scope, and submission. Mathematical correctness remains an evidence question rather than a workflow-status flag.

The top-level seven-stage state machine remains compatible with v0.1. New v0.2 capabilities are stage-owned contracts rather than additional routing stages.
