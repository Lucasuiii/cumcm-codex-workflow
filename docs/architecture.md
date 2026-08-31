# Architecture

The project uses files as the durable workflow state.

```text
official sources
  -> source manifest and problem facts
  -> task capabilities and model contract
  -> executable code and immutable run directory
  -> exact result index
  -> user-routed independent review package and imported review
  -> validation report, claim ledger, and figure manifest
  -> paper plan, reader narrative, and claims-evidence matrix
  -> clean paper plus sidecar traceability
  -> content, visible-text, rendered-page, and final review
  -> compile receipt and three-part delivery manifest
```

The Codex skill routes the active stage. `cumcm_check.py` validates local JSON Schemas and crosses stable IDs between artifacts. It records typed findings for structural, execution, numerical, semantic, and visual evidence. `record_decision.py` appends approvals bound to the current stage-owned contracts, so later edits invalidate the old approval without deleting its history. Decision events themselves are not hash-chained. Human review controls interpretation, model choice, claim scope, paper quality, and submission. Mathematical correctness remains an evidence question rather than a workflow-status flag.

Conversational Skill routing is the normal workspace entrypoint: the user supplies an official-input path, while Codex resolves the project identity and safe destination and invokes `init_project.py`. The script is the atomic execution layer. It stages a complete directory tree, copies regular official files without modifying their source, rejects symlinked or unsafe layouts, writes v0.4 state and a source manifest, records a machine-readable initialization receipt, and runs intake preflight before publishing the target directory. It deliberately stops at `awaiting_review`; later-stage facts and evidence are created only when those stages are reached.

Version 0.4 is the only accepted contract version. The top-level seven-stage state machine stays small; independent review is an entry gate within validation, and reader-facing QA is a subcontract within paper. The paper scaffold is generated from problem facts and the paper plan, while the validator checks its file inventory, per-question coverage, placeholders, compile engine, internal-metadata separation, and official-format review status.

SHA-256 is used only when byte identity changes the evidence: preserved official sources, formal computation inputs, claim-bearing outputs, approval scope, and the final reviewed PDF. Ordinary code, LaTeX, documentation, logs, caches, support files, and editing-stage figures rely on paths, Git/source revisions, executable checks, and human review unless a digest is explicitly useful.
