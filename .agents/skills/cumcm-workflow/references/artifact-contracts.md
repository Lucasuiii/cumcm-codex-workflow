# Artifact contracts

Read this reference when creating or validating v0.3 project files. The authoritative field shapes are the JSON Schemas in `../schemas/`.

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
| claim ledger | `validation/CLAIM_LEDGER.json` | validation |
| figure manifest | `figures/FIGURE_MANIFEST.json` | paper |
| paper plan | `paper/PAPER_PLAN.json` | paper |
| LaTeX template manifest | `paper/LATEX_TEMPLATE_MANIFEST.json` | paper |
| paper quality report | `paper/PAPER_QUALITY_REPORT.json` | paper |
| paper revision log | `paper/PAPER_REVISION_LOG.json` | paper |
| delivery manifest | `delivery/DELIVERY_MANIFEST.json` | delivery |
| compile receipt | `delivery/COMPILE_RECEIPT.json` | delivery |
| decision log | `.cumcm/decisions.jsonl` | cross-stage |

## Paper and decision contracts

The seven-stage state machine uses paper subcontracts rather than extra top-level stages. `PAPER_PLAN` records the claims-evidence matrix, nine-part per-question argument chain, reference review, figure jobs, and non-binding page budget. `LATEX_TEMPLATE_MANIFEST` inventories the modular source, maps subproblems, declares the engine and official-format review state, and names placeholder markers. `PAPER_QUALITY_REPORT` separates content, layout, and final QA and binds them to exact paper bytes. `PAPER_REVISION_LOG` preserves the first stable draft and quality-triggered revisions. `COMPILE_RECEIPT` preserves machine-readable attempts and binds selected output to the reviewed PDF.

Human approvals are append-only events in `.cumcm/decisions.jsonl`. Create them with `scripts/record_decision.py`; it hashes the current stage-owned artifacts and chains the event to its predecessor. People approve the visible artifact and summary, not a manually inspected digest. Do not put the mutable workflow state in decision scope. An old decision whose scoped artifact changed is stale and blocking.

`cumcm_check.py --gate-mode preflight` returns success only when remaining errors are purely missing human decisions; structural, execution, evidence, hash, claim, and version-binding failures still block. `--gate-mode enforce` also blocks on missing review.

## State vocabularies

Keep three state classes separate:

- workflow lifecycle: `not_started`, `in_progress`, `awaiting_review`, `passed`, `needs_revision`, `blocked`;
- evidence: `not_checked`, `missing_evidence`, `supported_not_reproduced`, `reproduced`, `partially_supported`, `contradicted`, `ambiguous`, `not_applicable`;
- review: `unreviewed`, `accepted`, `revision_requested`.

## Result and reproduction rules

An indexed scalar result uses `path#JSON-pointer` to identify its exact executed value. The checker compares the indexed value with that output. Classify each run file with `evidence_role`: inputs use `formal_input` or `auxiliary_input`; outputs use `claim_bearing_output`, `intermediate_output`, or `diagnostic_output`. Formal inputs and claim-bearing outputs require hashes. Auxiliary, intermediate, and diagnostic files may omit them. Every indexed result must resolve to an output of its declared run whose role is `claim_bearing_output`. Use the Git commit or source revision to identify code when available instead of hashing every source file.

Hash comparison is automatic. A digest mismatch remains blocking for official sources, formal run inputs, claim-bearing outputs, and frozen delivery files. Byte-size mismatch is stale metadata and produces a warning because a matching SHA-256 already establishes byte identity. Editing-stage figure drift also produces a warning; the final figure becomes blocking when it is listed in the delivery manifest. Logs, caches, temporary files, and LaTeX auxiliary files do not need hashes.

Every run input and output must declare `evidence_role`; absent roles are schema errors. `reproduced` is reserved for an isolated rerun with preserved inputs, environment, logs, outputs, hashes, and a claim-specific comparison.

Do not mix project IDs. Do not infer absent evidence. Do not mark a stage passed until every contract owned by that stage has an accepted review.
