---
name: cumcm-workflow
description: Build or resume a contest-ready CUMCM project from official files through modeling, one selected computation backend, bounded validation, fresh-context paper writing, and final delivery. Use for real CUMCM work; do not use for ordinary paper polishing or unsupported one-shot answers.
---

# CUMCM Workflow

Run a contest-native workflow whose important claims remain traceable to official sources and successful computation without turning every draft into an audit package.

## Start or resume

1. Locate `.cumcm/state.json`. Resume an exact `0.5.0` project. For a v0.4 workspace, offer `scripts/migrate_v04_to_v05.py`; migration copies into a new target, preserves the source, and requires claim-bearing computation to be rerun before finalizing.
2. If no state exists and the user supplies official files, read [01-intake.md](references/01-intake.md), choose a safe target, and run `scripts/init_project.py`. Do not make the user assemble the command.
3. Read only the active stage guide plus [handoffs.md](references/handoffs.md) when crossing stages. A fresh task reads its handoff first, not the entire workspace or old conversation.
4. Keep the six responsibilities distinct: orchestrator, modeling, computation, validation, paper, and delivery. Do not simulate separation by inventing many small Skills.

## Modes

- `working`: fast modeling, computation, debugging, and revision. Enforce official-input protection, real execution, exact result locators, code/output provenance, and non-fabrication. Missing final paper artifacts, review polish, or optional analyses do not block exploration.
- `finalizing`: freeze claim-bearing results, require current stage decisions and snapshots, fresh handoffs, bounded independent review, paper/PDF QA, and delivery binding.

`strict` and `sprint` remain compatible check profiles, but mode controls when formal gates apply. `enforce` in `working` reports `working_ready`; it is not a formal stage approval. In `finalizing`, `enforce` cannot pass unless every stage through the requested stage is marked `passed` and has a current accepted decision.

Switch modes with `scripts/set_mode.py`; entering finalizing reports the current preflight gaps instead of inventing approvals.

## Roles and handoffs

| Responsibility | Main reference | Outgoing handoff |
|---|---|---|
| Modeling | [02-problem-analysis.md](references/02-problem-analysis.md), [03-model-design.md](references/03-model-design.md) | `modeling-computation` |
| Computation | [04-computation.md](references/04-computation.md) | `computation-validation` |
| Validation | [05-validation.md](references/05-validation.md) | `validation-paper` |
| Paper | [06-paper-writing.md](references/06-paper-writing.md), [latex-template.md](references/latex-template.md) | `paper-delivery` |
| Delivery | [07-compile-delivery.md](references/07-compile-delivery.md) | final package |

Build handoffs with `scripts/build_handoff.py`. They contain canonical paths, compact downstream payloads, and an upstream digest. Do not copy full logs, failed runs, debug history, or old review conversations. A stale digest requires rebuilding the handoff. The paper→delivery handoff names the reviewed PDF, its compile-bound editable LaTeX snapshot, the formal computation source chain, and current official paper materials so a fresh delivery task does not rediscover them.

## Evidence gates

Treat findings by consequence:

- hard invariant / `P0`: wrong data or computation, task mismatch, unsupported key claim, code/result disagreement, stale provenance, fabricated approval/review, simulated data presented as observed, or final-version mismatch. These block.
- warning / `P1`: strong assumptions, weak baseline, incomplete validation or sensitivity, limited model fit, or a thin section. These remain visible but do not block.
- suggestion / `P2`: wording, layout, optional chart, or extra experiment. These do not enter the gate.

Independent validation uses `accepted`, `accepted_with_concerns`, `revision_required`, or `inconclusive`. Only an open P0 permits `revision_required`. After a full review finds P0 issues, the next package defaults to targeted re-review of those findings. A genuinely new P0 may still block; P1/P2 findings do not grow an endless blocking queue.

The independent review package contains only canonical evidence for formally indexed results: official inputs, problem/model contracts, `RESULTS_INDEX.json`, cited successful official runs, their source snapshots, formal inputs, claim-bearing outputs, and review instructions. Exclude failed/exploratory runs, stdout/stderr, full logs, and debug history. Targeted packages must carry the compact self-contained `TARGETED_FINDINGS.json`; do not copy the full prior review into the package. When building the paper brief, merge the compact structured review lineage newest-first so unresolved/accepted P1 findings from the full review survive a targeted P0-only result; resolved findings do not.

## Computation backend

Project state defaults to:

```json
{"preferred":"matlab","fallback":"python","selection":"auto"}
```

Use `scripts/backend_selection.py` or the same criteria to choose one backend for each official task. Consider numerical methods, optimization, ODE/PDE, signal processing, data cleaning, Excel/CSV work, machine learning, available toolboxes/packages, existing code, complexity, and runtime stability. MATLAB preference breaks ties; it is not mandatory. Detect MATLAB from explicit `implementation.matlab_executable`, PATH, then macOS `/Applications/MATLAB_R*.app/bin/matlab`. An unavailable preferred backend may fall back; an unavailable task `required_backend` must fail. Once selected, implement and officially run one language only. Do not create parity implementations unless the user explicitly requests them.

Every official run records the selected language, rationale, runtime, dependencies/toolboxes, entry point, source-tree snapshot, command, logs, inputs, outputs, assertions, and `official_run: true`. Results may cite only successful official runs and exact `path#JSON-pointer` values.

## Contest invariants

- Preserve and byte-identify official sources. OCR routes attention; rendered pages decide formulas, tables, and ambiguous notation.
- Never invent observed data, approvals, independent review, or successful execution. Label genuine simulations and record their generator and seed.
- Keep mathematical model and result contracts language-neutral.
- Use SHA-256 only for evidence-critical identity: official sources, formal inputs, claim-bearing outputs, compact snapshots/handoffs, review packages, selected source trees, and the reviewed final PDF.
- Keep internal IDs, evidence states, local paths, run coverage, and workflow language out of the visible paper.
- Paper handoff limitations come only from supported paper-eligible claim limitations, current P1 concerns, and explicit applicability/assumption/known-limitation fields—not contradicted claims or model scope. The paper task reads [06-paper-writing.md](references/06-paper-writing.md), makes `paper_structure` the semantic source of truth, and selects prose, equation, table, or figure by claim function. Reference papers are style priors only. A declared official paper template must be adopted/adapted before the generic scaffold; rule or submission-instruction documents do not block generic initialization and keep compliance unverified. No minimum figure/page count is a hard gate.
- Bind the final PDF to its reviewed bytes and to the exact editable LaTeX source snapshot used for compilation.
- Missing current official rules or templates blocks delivery; it does not authorize autonomous search or submission.
- Final delivery contains the reviewed PDF, editable LaTeX, and computation source as separate roles.

Read [artifact-contracts.md](references/artifact-contracts.md) when creating machine-readable files and [evidence-rules.md](references/evidence-rules.md) before model selection, review, or paper claims.

## Validate and revalidate

```bash
python3 scripts/cumcm_check.py --project <project> \
  --stage <stage> --profile strict --gate-mode enforce
```

For a known change, add repeated `--changed <path>` and one `--impact cosmetic|local|semantic|claim_changing|global`. The report gives the affected stages rather than defaulting to a full-workspace audit. Accepted decisions automatically create `.cumcm/snapshots/<stage>.json`; unchanged snapshots appear as trusted in the report. Hard invariants are still checked even when a snapshot is trusted.

Record a decision only after showing the exact artifact and receiving the decision:

```bash
python3 scripts/record_decision.py --project <project> --stage <stage> \
  --decision accepted --decision-id <id> --reviewer <name> \
  --task-turn-ref <ref> --summary <visible-summary>
```

Passing establishes current structure, provenance, successful execution, and recorded review boundaries. It does not prove mathematical correctness or global optimality.
