# CUMCM Codex Workflow

An evidence-bounded, reproducible, Codex-native workflow for the China Undergraduate Mathematical Contest in Modeling (CUMCM).

> Status: v0.2 evidence-contract implementation. Do not treat a passing workflow as proof that a model or paper is correct.

## Goals

- Keep the official problem statement and attachments as the factual source of record.
- Separate problem interpretation, model choice, computation, validation, and writing.
- Preserve runnable code, logs, environment metadata, machine-readable results, and claim evidence.
- Pause for human review at consequential modeling decisions.
- Resume from files on disk instead of relying on chat history.

## Workflow

```text
intake -> problem analysis -> model design -> computation
       -> validation -> paper writing -> compile and delivery
```

The repository contains one repo-scoped Codex skill at
`.agents/skills/cumcm-workflow`. Invoke it explicitly with `$cumcm-workflow`,
or let Codex select it when the task clearly concerns a CUMCM project.

## Version 0.2

Version 0.2 provides:

- a concise workflow router;
- stage-specific references;
- eleven versioned JSON Schemas covering workflow state and the ten evidence artifacts;
- a vertical evidence chain from official facts through capabilities, models, runs, results, claims, and figures;
- deterministic checks for local schemas, hashes, source traceability, model ownership, real run outputs, exact result locators, cross-question consistency, strong-claim certificates, figure provenance, and delivery;
- `strict` and `sprint` profiles that share non-negotiable evidence gates;
- stable diagnostic IDs and a machine-readable validation report;
- a minimal XeLaTeX template;
- executable regressions based on a known policy-scope failure mode.

Final `model-xray` auditing remains an explicit, deferred hook rather than an automatic step.

Hash checks are artifact-specific: official inputs, run records declared as `formal_input` or `claim_bearing_output`, and frozen delivery files remain blocking. Auxiliary, intermediate, and diagnostic run files may omit hashes; editing-stage figure drift and redundant byte-size mismatches are warnings. Digests are recorded and compared automatically, not manually inspected.

See [docs/v0.2-design.md](docs/v0.2-design.md) for contract fields, evidence boundaries, profile behavior, migration rules, and release criteria.

## Validate a project

```bash
python3 .agents/skills/cumcm-workflow/scripts/cumcm_check.py \
  --project /path/to/project \
  --stage validation \
  --profile strict
```

The command writes `.cumcm/validation-report.json`. Exit code `0` means the implemented structural, execution, numerical-trace, semantic-contract, and visual-review gates found no errors. It is not a mathematical correctness certificate.

## Quick validation

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/cumcm-workflow
```

The second command uses the bundled Codex validator when available. The Python package requires Python 3.10+ and `jsonschema>=4.18`.

## Provenance and licensing

This repository is independently designed and authored for reproducible CUMCM work. See [docs/provenance.md](docs/provenance.md).

No open-source license is granted yet. A license will be selected after the provenance review is complete.

## Safety boundary

- Never invent empirical data to make a preferred method look better.
- Never call an approximate or restricted-class result globally optimal without a certificate and a declared scope.
- Never write paper claims that are not traceable to executed outputs.
- Never treat schema checks, keyword matches, or solver success flags as proof of mathematical correctness.
