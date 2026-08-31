# Artifact contracts

Read this reference when creating or validating v0.4 project files. The authoritative field shapes are the JSON Schemas in `../schemas/`.

## Common envelope

Every contract declares:

- `schema_version` matching the project's supported workflow version;
- a fixed `artifact_type`;
- one shared `project_id`;
- serialization time and producer;
- a review decision: `unreviewed`, `accepted`, or `revision_requested`.

Automated validators may create or update an artifact, but they may not set a human review to `accepted`.

## Stable identifiers

Use stable IDs such as `SRC-001`, `FACT-Q1-001`, `CAP-Q1-001`, `MODEL-Q1-001`, `RUN-Q1-...`, `RES-Q1-001`, `CLM-Q1-001`, and `FIG-Q1-001`. Once referenced, an ID is immutable even when its prose label changes.

## Canonical paths

| Contract | Path | Owner |
|---|---|---|
| workflow state | `.cumcm/state.json` | intake |
| source manifest | `problem/SOURCE_MANIFEST.json` | intake |
| problem facts | `analysis/PROBLEM_FACTS.json` | problem analysis |
| task capabilities | `analysis/TASK_CAPABILITIES.json` | problem analysis |
| model contract | `model/MODEL_CONTRACT.json` | model design |
| cross-question ledger | `model/CROSS_QUESTION_LEDGER.json` | model design |
| run manifest | `runs/<run-id>/RUN_MANIFEST.json` | computation |
| results index | `results/RESULTS_INDEX.json` | computation |
| independent review package | `validation/independent-review-package/REVIEW_PACKAGE_MANIFEST.json` | validation entry gate |
| independent review result | `validation/INDEPENDENT_REVIEW_RESULT.json` | validation entry gate |
| claim ledger | `validation/CLAIM_LEDGER.json` | validation |
| figure manifest | `figures/FIGURE_MANIFEST.json` | paper |
| paper plan | `paper/PAPER_PLAN.json` | paper |
| LaTeX template manifest | `paper/LATEX_TEMPLATE_MANIFEST.json` | paper |
| paper quality report | `paper/PAPER_QUALITY_REPORT.json` | paper |
| paper revision log | `paper/PAPER_REVISION_LOG.json` | paper |
| paper traceability sidecar | `paper/PAPER_TRACEABILITY.json` | paper |
| visible-text report | `paper/PAPER_VISIBLE_TEXT_REPORT.json` | paper |
| delivery manifest | `delivery/DELIVERY_MANIFEST.json` | delivery |
| compile receipt | `delivery/COMPILE_RECEIPT.json` | delivery |
| decision log | `.cumcm/decisions.jsonl` | cross-stage |

## Paper and decision contracts

The seven-stage state machine uses subcontracts rather than extra top-level stages. Before validation, the review-package and review-result contracts enforce user-routed context separation. `PAPER_PLAN` records the reader narrative, claims-evidence matrix, nine-part per-question argument chain, reference review, figure jobs, and non-binding page budget. `PAPER_TRACEABILITY` keeps stable IDs in a non-rendered sidecar. `PAPER_VISIBLE_TEXT_REPORT` checks the actual PDF for internal metadata and numerical-presentation risks. `PAPER_QUALITY_REPORT` separates reader-facing content, layout, and final QA and binds them to exact paper bytes. `PAPER_REVISION_LOG` preserves quality-triggered revisions. `COMPILE_RECEIPT` preserves machine-readable attempts and binds selected output to the reviewed PDF.

Human approvals are append-only events in `.cumcm/decisions.jsonl`. Create them with `scripts/record_decision.py`; it binds the current stage-owned contracts so later edits can invalidate an approval. v0.4 does not hash-chain decision events themselves. People approve the visible artifact and summary, not a manually inspected digest. Do not put mutable workflow state in decision scope. A later `revision_requested` event supersedes an earlier acceptance.

`cumcm_check.py --gate-mode preflight` returns success only when remaining errors are purely missing human decisions; structural, execution, evidence, hash, claim, and version-binding failures still block. `--gate-mode enforce` also blocks on missing review.

## State vocabularies

Keep three state classes separate:

- workflow lifecycle: `not_started`, `in_progress`, `awaiting_review`, `passed`, `needs_revision`, `blocked`;
- evidence: `not_checked`, `missing_evidence`, `supported_not_reproduced`, `reproduced`, `partially_supported`, `contradicted`, `ambiguous`, `not_applicable`;
- review: `unreviewed`, `accepted`, `revision_requested`.

## Result and reproduction rules

An indexed scalar result uses `path#JSON-pointer` to identify its exact executed value. The checker compares the indexed value with that output. Classify each run file with `evidence_role`: inputs use `formal_input` or `auxiliary_input`; outputs use `claim_bearing_output`, `intermediate_output`, or `diagnostic_output`. Formal inputs and claim-bearing outputs require hashes. Auxiliary, intermediate, and diagnostic files may omit them. Every indexed result must resolve to an output of its declared run whose role is `claim_bearing_output`. Use the Git commit or source revision to identify code when available instead of hashing every source file.

Hash comparison is automatic and deliberately narrow. A digest remains blocking for official sources, formal run inputs, claim-bearing outputs, decision-scope contracts, and the exact reviewed final PDF. Ordinary code and LaTeX files use the Git/source revision plus compile or rerun checks. Editing-stage figures, documentation, delivery support files, logs, caches, temporary files, and LaTeX auxiliaries do not require hashes. Optional stale digests on those artifacts are warnings only.

Every run input and output must declare `evidence_role`; absent roles are schema errors. `reproduced` is reserved for an isolated rerun with preserved inputs, environment, logs, claim-bearing outputs, the required formal-input/output digests, and a claim-specific comparison.

Do not mix project IDs. Do not infer absent evidence. Do not mark a stage passed until every contract owned by that stage has an accepted review.
