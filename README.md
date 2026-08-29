# CUMCM Codex Workflow

An evidence-bounded, reproducible, Codex-native workflow for the China Undergraduate Mathematical Contest in Modeling (CUMCM).

> Status: early public scaffold. Do not treat a completed workflow as proof that a model or paper is correct.

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

## Current scope

Version 0.1 provides:

- a concise workflow router;
- stage-specific references;
- artifact and evidence contracts;
- deterministic validators for inventories, state, facts, results, claims, and delivery;
- a minimal XeLaTeX template;
- a regression contract based on a known policy-scope failure mode.

Final paper auditing is intentionally deferred. No `model-xray` integration is included yet.

## Quick validation

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/cumcm-workflow
```

The second command uses the bundled Codex validator when available.

## Provenance and licensing

This repository is an original implementation informed by general workflow ideas such as staged execution, checkpoints, resumability, and artifact contracts. It contains no decrypted Modex skills, proprietary templates, binaries, activation material, or copied closed-source scripts. See [docs/provenance.md](docs/provenance.md).

No open-source license is granted in this initial scaffold. A license will be selected after the provenance review is complete.

## Safety boundary

- Never invent empirical data to make a preferred method look better.
- Never call an approximate or restricted-class result globally optimal without a certificate and a declared scope.
- Never write paper claims that are not traceable to executed outputs.
- Never treat schema checks, keyword matches, or solver success flags as proof of mathematical correctness.
