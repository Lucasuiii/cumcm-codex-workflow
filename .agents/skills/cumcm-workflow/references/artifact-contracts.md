# Artifact contracts

Read this reference when creating, migrating, or validating v0.2 project files. The authoritative field shapes are the JSON Schemas in `../schemas/`.

## Common envelope

Every contract declares:

- `schema_version: "0.2.0"`;
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
| delivery manifest | `delivery/DELIVERY_MANIFEST.json` | delivery |

## State vocabularies

Keep three state classes separate:

- workflow lifecycle: `not_started`, `in_progress`, `awaiting_review`, `passed`, `needs_revision`, `blocked`;
- evidence: `not_checked`, `missing_evidence`, `supported_not_reproduced`, `reproduced`, `partially_supported`, `contradicted`, `ambiguous`, `not_applicable`;
- review: `unreviewed`, `accepted`, `revision_requested`.

## Result and reproduction rules

An indexed scalar result uses `path#JSON-pointer` to identify its exact executed value. The checker compares the indexed value with that output. Classify each run file with `evidence_role`: inputs use `formal_input` or `auxiliary_input`; outputs use `claim_bearing_output`, `intermediate_output`, or `diagnostic_output`. Formal inputs and claim-bearing outputs require hashes. Auxiliary, intermediate, and diagnostic files may omit them. Every indexed result must resolve to an output of its declared run whose role is `claim_bearing_output`. Use the Git commit or source revision to identify code when available instead of hashing every source file.

Hash comparison is automatic. A digest mismatch remains blocking for official sources, formal run inputs, claim-bearing outputs, and frozen delivery files. Byte-size mismatch is stale metadata and produces a warning because a matching SHA-256 already establishes byte identity. Editing-stage figure drift also produces a warning; the final figure becomes blocking when it is listed in the delivery manifest. Logs, caches, temporary files, and LaTeX auxiliary files do not need hashes.

For backward compatibility, a v0.2 run record without `evidence_role` is interpreted conservatively: an input defaults to `formal_input` and an output defaults to `claim_bearing_output`. Existing v0.2 manifests therefore remain valid and strict; new or edited manifests should declare the role explicitly.

`reproduced` is reserved for an isolated rerun with preserved inputs, environment, logs, outputs, hashes, and a claim-specific comparison. Map the legacy v0.1 status `supported` to `supported_not_reproduced`, never to `reproduced`.

## Migration from v0.1

Keep the seven stage names. Add `workflow_version: "0.2.0"` and the common envelope to state. Preserve v0.1 files in version control or backups, and migrate `TASK_CONTRACT.json` into explicit capabilities without inventing missing acceptance checks, code entry points, or result IDs.

Absent fields are migration findings, not values to infer. Do not mix project IDs. Do not mark a stage passed until every contract owned by that stage has an accepted review.
