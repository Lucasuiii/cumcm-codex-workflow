---
name: cumcm-workflow
description: Build or resume a CUMCM mathematical-modeling project from official problem files through modeling, executed computation, validation, LaTeX writing, and delivery. Use for Chinese undergraduate mathematical-modeling competition work; do not use for ordinary paper polishing or unsupported one-shot answer generation.
---

# CUMCM Workflow

Create a reproducible contest project whose conclusions remain traceable to official sources and executed results.

## Start or resume

1. Locate `.cumcm/state.json`. If it declares workflow version `0.2.0`, validate through the recorded stage with `scripts/cumcm_check.py` and resume there.
2. If it is a v0.1 state, preserve it and follow the migration rules in [references/artifact-contracts.md](references/artifact-contracts.md). Never infer missing v0.2 evidence.
3. If no state exists, read [references/01-intake.md](references/01-intake.md) and initialize the project from copied official inputs.
4. Use the `strict` profile by default. Use `sprint` only when the user prioritizes contest-time speed; it may reduce exploration and polish but never source, execution, consistency, or claim checks.
5. Load only the reference for the active stage. Do not load every stage guide at once.
6. Validate required artifacts before advancing. A conflict returns to its earliest owning stage and blocks dependent stages without deleting their artifacts.

## Stages

| Stage | Reference | Human gate |
|---|---|---|
| `intake` | [01-intake.md](references/01-intake.md) | no |
| `problem-analysis` | [02-problem-analysis.md](references/02-problem-analysis.md) | approve facts, interpretation, and capabilities |
| `model-design` | [03-model-design.md](references/03-model-design.md) | choose model, dependencies, and scope |
| `computation` | [04-computation.md](references/04-computation.md) | approve preserved runs and indexed results |
| `validation` | [05-validation.md](references/05-validation.md) | approve evidence states, limitations, and claims |
| `paper` | [06-paper-writing.md](references/06-paper-writing.md) | approve final content |
| `delivery` | [07-compile-delivery.md](references/07-compile-delivery.md) | approve submission package |

## Invariants

- Treat the official statement and official attachments as the factual source of record.
- OCR routes attention; rendered pages decide formulas, tables, and ambiguous notation.
- Preserve raw inputs. Write generated artifacts into separate stage directories.
- Do not advance past a human gate without explicit approval.
- Do not invent observed data. Mark genuine simulations as `simulated` and record their generator and seed.
- Run code before citing its output. Preserve commands, exit status, logs, environment, and output hashes.
- Link sources, facts, capabilities, model components, runs, results, claims, and figures with stable IDs rather than prose matching.
- State the feasible set, policy class, approximation, and certificate behind every optimality claim.
- Paper text may summarize validated artifacts but may not create new numerical results.
- Schema or keyword checks establish structure only, never mathematical truth.

Read [references/artifact-contracts.md](references/artifact-contracts.md) when creating or validating project files. Read [references/evidence-rules.md](references/evidence-rules.md) before model selection, claim review, or paper writing.

## Validate

From the Skill directory, run:

```bash
python scripts/cumcm_check.py --project <project> --stage <stage> --profile strict
```

The report is written to `.cumcm/validation-report.json`. A zero exit code means the declared contracts and evidence links passed the implemented checks; it is not a correctness certificate.

## Final audit hook

Version 0.2 exports stable claim and run contracts for a later audit. Record final `model-xray` audit as deferred unless the user explicitly requests it; do not invoke it automatically.
