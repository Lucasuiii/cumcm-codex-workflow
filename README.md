# CUMCM Codex Workflow

An evidence-bounded, reproducible, Codex-native workflow for the China Undergraduate Mathematical Contest in Modeling (CUMCM).

> Status: v0.3. This release accepts only v0.3 project contracts. A passing workflow is not proof that a model or paper is correct.

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

## Version 0.3

Version 0.3 provides:

- a paper plan with reference review, Claims-Evidence Matrix, nine-part per-question argument chains, and figure jobs;
- separate content, layout, and final-QA reviews bound to exact paper bytes;
- quality-triggered revision snapshots and P0/P1/P2 issue tracking;
- a machine-readable compile receipt bound to the reviewed PDF and delivery summary;
- append-only, artifact-bound human decisions instead of silently editable approval fields;
- `preflight` and `enforce` gate modes, so automation can prepare a human review without weakening evidence failures;
- a modular CTeX paper scaffold with generated per-question sections, explicit placeholders, and an official-format review gate.

The seven workflow stages and the evidence chain from official facts through capabilities, models, runs, results, claims, figures, and delivery remain unchanged.

Final `model-xray` auditing remains an explicit, deferred hook rather than an automatic step.

Hash checks are artifact-specific: official inputs, run records declared as `formal_input` or `claim_bearing_output`, and frozen delivery files remain blocking. Auxiliary, intermediate, and diagnostic run files may omit hashes; editing-stage figure drift and redundant byte-size mismatches are warnings. Digests are recorded and compared automatically, not manually inspected.

See [docs/v0.3-design.md](docs/v0.3-design.md) for the complete design and [docs/workflow-contract.md](docs/workflow-contract.md) for stage gates.

Initialize the paper scaffold after `PAPER_PLAN.json` and `PROBLEM_FACTS.json` agree on every subproblem:

```bash
python3 .agents/skills/cumcm-workflow/scripts/init_latex_paper.py \
  --project /path/to/project \
  --competition-year 2026 \
  --title "论文题目"
```

The bundled scaffold is a submission-neutral writing structure. Before delivery, compare it with the current official competition package and record `official_compliance=verified_against_current_rules` with the exact source used.

## Validate a project

```bash
python3 .agents/skills/cumcm-workflow/scripts/cumcm_check.py \
  --project /path/to/project \
  --stage validation \
  --profile strict \
  --gate-mode enforce
```

The command writes `.cumcm/validation-report.json`. `preflight` may return zero with `gate_status=awaiting_review` only when all remaining errors are human-gate items. `enforce` requires those approvals as well. Neither mode is a mathematical correctness certificate.

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
