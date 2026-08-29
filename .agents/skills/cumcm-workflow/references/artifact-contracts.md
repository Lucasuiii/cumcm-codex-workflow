# Artifact contracts

## Workflow state

`.cumcm/state.json` contains `current_stage` and a status for every stage. Valid statuses are `not_started`, `in_progress`, `awaiting_review`, `passed`, `needs_revision`, and `blocked`.

## Problem facts

`PROBLEM_FACTS.json` contains:

```json
{
  "problem_id": "year-letter",
  "source_files": ["problem/official.pdf"],
  "subproblems": [{"id": "Q1", "request": "..."}],
  "facts": [{"id": "F1", "statement": "...", "source": "problem/official.pdf#page=1"}]
}
```

## Run manifest

`RUN_MANIFEST.json` identifies a real execution: run ID, command, status, timestamps, inputs, outputs, and exit code. Referenced outputs must exist and be nonempty.

## Claim ledger

`CLAIM_LEDGER.json` contains claims with unique IDs, allowed statuses, scope, and at least one evidence path for supported claims.

## Delivery manifest

`DELIVERY_MANIFEST.json` lists final relative paths and optional SHA-256 hashes. Every listed file must exist and be nonempty.
