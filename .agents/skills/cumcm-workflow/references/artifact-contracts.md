# Artifact contracts

Read this reference when creating or checking v0.5 files. JSON Schemas define core machine-readable shapes, but a schema mismatch is important only when it prevents reliable interpretation of evidence.

## Canonical artifacts

| Responsibility | Canonical files |
|---|---|
| Workflow | `.cumcm/state.json`, `.cumcm/decisions.jsonl`, `.cumcm/snapshots/<stage>.json` |
| Intake/modeling | `SOURCE_MANIFEST.json`, `PROBLEM_FACTS.json`, `TASK_CAPABILITIES.json`, `MODEL_CONTRACT.json`, `CROSS_QUESTION_LEDGER.json` |
| Computation | `runs/<id>/RUN_MANIFEST.json`, `RESULTS_INDEX.json` |
| Validation | independent review package/result, `CLAIM_LEDGER.json` |
| Paper | `PAPER_PLAN.json`, `LATEX_TEMPLATE_MANIFEST.json`, `PAPER_QUALITY_REPORT.json`, `PAPER_TRACEABILITY.json`, `PAPER_VISIBLE_TEXT_REPORT.json` |
| Delivery | `COMPILE_RECEIPT.json`, `DELIVERY_MANIFEST.json` |
| Cross-stage | `handoffs/<transition>/HANDOFF.json` |

The optional common `review` envelope remains accepted for compatibility, but formal stage approval lives in the append-only decision log. Recording an accepted decision automatically writes a derived stage snapshot. Snapshot files require no human fields and can be regenerated from the accepted scope.

## Evidence-critical bindings

- Official sources, formal inputs, and claim-bearing outputs use file hashes.
- Official computation uses one canonical resolution in handoffs and review packaging: `RESULTS_INDEX.json` → referenced successful official run → current selected source-tree snapshot. Broken links fail rather than being omitted.
- Review packages bind packaged files and the live upstream sources.
- Handoffs bind only canonical downstream inputs.
- Paper compilation binds the exact final PDF and the exact editable source tree.

Stable IDs and exact result locators remain important. Paper plans and quality reports are intentionally lighter: they record claims, representations, structure, P0/P1/P2, and version bindings rather than fixed counts or exhaustive quality dimensions.

## Modes and migration

Working mode permits incomplete downstream contracts. Finalizing requires current decisions, snapshots, handoffs, review, PDF QA, and delivery. `migrate_v04_to_v05.py` copies a v0.4 workspace into a v0.5 working workspace and marks migrated runs non-official; it never infers that old computation is current enough for final claims.
