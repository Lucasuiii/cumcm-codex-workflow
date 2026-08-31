---
name: cumcm-workflow
description: Build or resume a CUMCM mathematical-modeling project from official problem files through modeling, executed computation, validation, LaTeX writing, and delivery. Use for Chinese undergraduate mathematical-modeling competition work; do not use for ordinary paper polishing or unsupported one-shot answer generation.
---

# CUMCM Workflow

Create a reproducible contest project whose conclusions remain traceable to official sources and executed results.

## Start or resume

1. Locate `.cumcm/state.json`. Resume only when it declares exact workflow version `0.4.0`; otherwise stop and report that the project is outside this Skill's accepted contract.
2. If no state exists and the user asks to initialize from a local official-input path, read [references/01-intake.md](references/01-intake.md), resolve the project ID and a safe target, and run `scripts/init_project.py` for them. Do not make the user assemble or execute the command.
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
| `validation` | [05-validation.md](references/05-validation.md) | first route a packaged review to a user-selected separate reviewer, then approve evidence states, limitations, and claims |
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
- Internal IDs, evidence states, run coverage, paths, and gate language belong in sidecars and must not render in the final paper.
- For each subproblem, preserve the chain from interpretation and assumptions through derivation, computation, results, validation, and limitations. Do not use page count or figure count as a quality certificate.
- Human decisions are append-only and artifact-bound. If an approved artifact changes, obtain a new decision; do not rewrite history.
- Schema or keyword checks establish structure only, never mathematical truth.
- Official compliance uses user-supplied materials only. Missing rules or templates block delivery and never authorize autonomous web search.
- Require final PDF, editable LaTeX source, and computation source as separate delivery roles.
- Use SHA-256 only where byte identity is evidence-critical: official sources, formal inputs, claim-bearing outputs, decision scope, and the reviewed final PDF.

Read [references/artifact-contracts.md](references/artifact-contracts.md) when creating or validating project files. Read [references/evidence-rules.md](references/evidence-rules.md) before model selection, claim review, or paper writing.

## Initialize from conversation

The normal interface is a Codex request containing the official file or directory path, for example: `请初始化国赛项目，官方题目和附件在 /absolute/path/to/2026B题。` Explicit `$cumcm-workflow` invocation is optional when the intent is already clear.

When that intent and path are present, initialize autonomously:

1. Inspect the supplied path read-only. Treat a supplied file as the input set requested by the user; treat a supplied directory as the bundle to inventory. Do not silently add neighboring files.
2. Infer a stable ID such as `CUMCM-2026-B` from explicit conversation context, path names, filenames, or the visible statement title. Ask one short question only if the competition year/problem identifier is still genuinely ambiguous.
3. Use a user-specified target when present. Otherwise choose a sibling directory named from the normalized ID, such as `cumcm-2026-b-workspace`. If it is non-empty, stop and ask for a target instead of overwriting it or silently creating duplicates.
4. Resolve `scripts/init_project.py` relative to this Skill and run it with absolute paths, the inferred ID, and `strict` profile. The initialization request authorizes creation of this new local workspace; it does not authorize approval of the intake gate.
5. Read the generated initialization and validation reports. Tell the user the absolute project path, copied-source count, ignored operating-system metadata, gate status, and the exact artifacts awaiting review.

The script copies but never deletes or edits official inputs. It creates the complete directory layout, v0.4 state, source manifest, project brief, initialization receipt, and intake preflight report. It does not infer problem facts, models, results, reviews, or decisions.

The command-line form is an internal/maintainer interface, not a required user step:

```bash
python3 scripts/init_project.py --project <new-project> \
  --project-id <stable-id> --official <official-file-or-directory>
```

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
