---
name: cumcm-workflow
description: Build or resume a CUMCM mathematical-modeling project from official problem files through modeling, executed computation, validation, LaTeX writing, and delivery. Use for Chinese undergraduate mathematical-modeling competition work; do not use for ordinary paper polishing or unsupported one-shot answer generation.
---

# CUMCM Workflow

Create a reproducible contest project whose conclusions remain traceable to official sources and executed results.

## Start or resume

1. Locate `.cumcm/state.json`. Resume only when it declares exact workflow version `0.3.0`; otherwise stop and report that the project is outside this Skill's accepted contract.
2. If no state exists, read [references/01-intake.md](references/01-intake.md) and initialize the project from copied official inputs.
3. Use the `strict` profile by default. Use `sprint` only when the user prioritizes contest-time speed; it may reduce exploration and polish but never source, execution, consistency, or claim checks.
4. Load only the reference for the active stage. Do not load every stage guide at once.
5. Validate required artifacts before advancing. A conflict returns to its earliest owning stage and blocks dependent stages without deleting their artifacts.

## Stages

| Stage | Reference | Human gate |
|---|---|---|
| `intake` | [01-intake.md](references/01-intake.md) | confirm the official input set and source-manifest review |
| `problem-analysis` | [02-problem-analysis.md](references/02-problem-analysis.md) | approve facts, interpretation, and capabilities |
| `model-design` | [03-model-design.md](references/03-model-design.md) | choose model, dependencies, and scope |
| `computation` | [04-computation.md](references/04-computation.md) | approve preserved runs and indexed results |
| `validation` | [05-validation.md](references/05-validation.md) | approve evidence states, limitations, and claims |
| `paper` | [06-paper-writing.md](references/06-paper-writing.md) and [latex-template.md](references/latex-template.md) | approve the modular source, version-bound content, layout, and issue closure |
| `delivery` | [07-compile-delivery.md](references/07-compile-delivery.md) | approve the compiled, visually reviewed submission package |

## Invariants

- Treat the official statement and official attachments as the factual source of record.
- OCR routes attention; rendered pages decide formulas, tables, and ambiguous notation.
- Preserve raw inputs. Write generated artifacts into separate stage directories.
- Do not advance past a human gate without explicit approval.
- Do not invent observed data. Mark genuine simulations as `simulated` and record their generator and seed.
- Run code before citing its output. Preserve commands, exit status, logs, environment, and hashes for formal inputs and claim-bearing outputs.
- Let tools record and compare digests; never require a person to inspect or confirm a 64-character hash manually.
- Link sources, facts, capabilities, model components, runs, results, claims, and figures with stable IDs rather than prose matching.
- State the feasible set, policy class, approximation, and certificate behind every optimality claim.
- Paper text may summarize validated artifacts but may not create new numerical results.
- For each subproblem, preserve the chain from interpretation and assumptions through derivation, computation, results, validation, and limitations. Do not use page count or figure count as a quality certificate.
- Human decisions are append-only and artifact-bound. If an approved artifact changes, obtain a new decision; do not rewrite history.
- Schema or keyword checks establish structure only, never mathematical truth.

Read [references/artifact-contracts.md](references/artifact-contracts.md) when creating or validating project files. Read [references/evidence-rules.md](references/evidence-rules.md) before model selection, claim review, or paper writing.

## Validate

From the Skill directory, run:

```bash
python3 scripts/cumcm_check.py --project <project> --stage <stage> --profile strict --gate-mode enforce
```

Use `--gate-mode preflight` while preparing a review: it may return zero only when automated checks pass and the remaining findings are human decisions. Use `enforce` before advancing or delivery. The report is written to `.cumcm/validation-report.json`. A zero exit code means the applicable automated and gate-mode checks passed; it is not a correctness certificate.

Record an explicit decision only after showing the reviewer the exact artifacts and receiving their decision:

```bash
python3 scripts/record_decision.py --project <project> --stage <stage> \
  --decision accepted --decision-id <unique-id> --reviewer <name> \
  --task-turn-ref <turn-ref> --summary <user-visible-summary>
```

## Final audit hook

The workflow exports stable claim, run, paper-quality, and delivery contracts for a later audit. Record final `model-xray` audit as deferred unless the user explicitly requests it; do not invoke it automatically.
