---
name: cumcm-workflow
description: Build or resume a CUMCM mathematical-modeling project from official problem files through modeling, executed computation, validation, LaTeX writing, and delivery. Use for Chinese undergraduate mathematical-modeling competition work; do not use for ordinary paper polishing or unsupported one-shot answer generation.
---

# CUMCM Workflow

Create a reproducible contest project whose conclusions remain traceable to official sources and executed results.

## Start or resume

1. Locate `.cumcm/state.json`. If it exists, validate it with `scripts/validate_stage_state.py` and resume the recorded stage.
2. If no state exists, read [references/01-intake.md](references/01-intake.md) and initialize the project from copied official inputs.
3. Load only the reference for the active stage. Do not load every stage guide at once.
4. Validate required artifacts before advancing. A missing or invalid artifact sends the project back to the stage that owns it.

## Stages

| Stage | Reference | Human gate |
|---|---|---|
| `intake` | [01-intake.md](references/01-intake.md) | no |
| `problem-analysis` | [02-problem-analysis.md](references/02-problem-analysis.md) | approve interpretation |
| `model-design` | [03-model-design.md](references/03-model-design.md) | choose model and scope |
| `computation` | [04-computation.md](references/04-computation.md) | approve completed runs |
| `validation` | [05-validation.md](references/05-validation.md) | approve supported claims |
| `paper` | [06-paper-writing.md](references/06-paper-writing.md) | approve final content |
| `delivery` | [07-compile-delivery.md](references/07-compile-delivery.md) | approve submission package |

## Invariants

- Treat the official statement and official attachments as the factual source of record.
- OCR routes attention; rendered pages decide formulas, tables, and ambiguous notation.
- Preserve raw inputs. Write generated artifacts into separate stage directories.
- Do not advance past a human gate without explicit approval.
- Do not invent observed data. Mark genuine simulations as `simulated` and record their generator and seed.
- Run code before citing its output. Preserve commands, exit status, logs, environment, and output hashes.
- State the feasible set, policy class, approximation, and certificate behind every optimality claim.
- Paper text may summarize validated artifacts but may not create new numerical results.
- Schema or keyword checks establish structure only, never mathematical truth.

Read [references/artifact-contracts.md](references/artifact-contracts.md) when creating or validating project files. Read [references/evidence-rules.md](references/evidence-rules.md) before model selection, claim review, or paper writing.

## Final audit

Version 0.1 stops after delivery verification. Record final audit as deferred; do not invoke `model-xray` automatically.
