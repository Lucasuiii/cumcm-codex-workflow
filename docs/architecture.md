# Architecture

The project uses files as the durable workflow state.

```text
official sources
  -> source manifest and problem facts
  -> task contract and model specification
  -> executable code and immutable run directory
  -> validation report and claim ledger
  -> figures and LaTeX paper
  -> delivery manifest
```

The Codex skill routes the active stage. Deterministic scripts validate structure, paths, hashes, and declared relationships. Human review controls interpretation, model choice, claim scope, and submission. Mathematical correctness remains an evidence question rather than a workflow-status flag.
