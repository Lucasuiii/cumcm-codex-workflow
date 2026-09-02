# CUMCM Codex Workflow

English | [简体中文](README.zh-CN.md)

A contest-native, evidence-focused, low-friction Codex workflow for the China Undergraduate Mathematical Contest in Modeling.

> Current release: **v0.5**. Passing checks establishes current provenance, execution, and workflow consistency—not mathematical correctness.

## 1. Why v0.5

v0.5 keeps the strongest parts of v0.4—official-source protection, executed computation, exact result locators, claim-bearing output tracking, final-PDF binding, decision records, reproducibility, and limitations—while removing audit-shaped friction from ordinary contest work.

- Hard invariants remain blocking.
- Model-strength concerns become warnings.
- Presentation suggestions do not enter the gate.
- Paper writing moves to a fresh-context task through a compact handoff.
- MATLAB and Python are selected by task fit; one official task uses one official implementation by default.
- Approved unchanged stages use trusted snapshots instead of repeated full review.

## 2. Architecture

```text
orchestrator
  -> modeling
  -> computation (MATLAB or Python)
  -> independent validation
  -> fresh paper task
  -> delivery
```

These are responsibilities, not a large collection of micro-Skills. The main `cumcm-workflow` Skill routes the work; the existing packaged Reviewer Skill handles context-separated validation.

The durable interfaces are four handoffs:

```text
modeling-computation
computation-validation
validation-paper
paper-delivery
```

## 3. Modes and evidence gates

`working` is the default. It protects official inputs, requires real execution before citation, checks source/result provenance and exact locators, and prevents fabricated data or approvals. It does not require final paper artifacts, full review polish, or optional validation during exploration.

`finalizing` freezes claim-bearing results and activates accepted stage decisions/snapshots, fresh handoffs, independent validation, paper/PDF QA, and delivery binding.

Findings are classified by consequence:

| Level | Meaning | Gate |
|---|---|---|
| Hard invariant / P0 | real data/computation error, task mismatch, unsupported key claim, stale provenance, fabricated review, or final-version mismatch | blocking |
| Warning / P1 | assumptions, baseline, model fit, sensitivity, or validation concern | non-blocking |
| Suggestion / P2 | wording, optional chart, layout refinement, or extra experiment | outside the gate |

`enforce` cannot be bypassed by editing state: in finalizing mode, every stage through the requested stage must be `passed` and covered by a current accepted decision.

## 4. Fresh tasks and handoffs

`build_handoff.py` creates a compact `HANDOFF.json` with canonical artifact paths/hashes, an upstream digest, and a stage-specific payload. It excludes full logs, failed runs, debug transcripts, and old review conversations.

The paper handoff contains:

- problem and model summaries;
- verified results and selected claims;
- limitations;
- a draft figure/table representation plan;
- identified official-format files.

A new task reads the handoff first. If a canonical upstream artifact changes, the handoff becomes stale and must be rebuilt.

## 5. Independent validation

The first review is full and context-separated. The package binds both copied materials and live upstream artifacts with digests. The user records different originating/reviewer task references. Same-model fresh-context review remains correlated; task metadata improves evidence but cannot prove human or model independence cryptographically.

Verdicts are:

- `accepted`
- `accepted_with_concerns`
- `revision_required`
- `inconclusive`

Only an open P0 permits `revision_required`. After a full review finds P0 issues, the next package defaults to targeted re-review of every prior open P0. New P1/P2 findings remain non-blocking; a genuinely new evidenced P0 may still block.

## 6. MATLAB and Python

New projects default to:

```json
{"preferred":"matlab","fallback":"python","selection":"auto"}
```

MATLAB preference is a tie-break, not a mandate. Selection considers numerical linear algebra, optimization, ODE/PDE, signal processing, data cleaning, Excel/CSV processing, machine learning, toolboxes/packages, existing code, complexity, and runtime stability.

Once selected, only that backend is officially implemented and run. If it cannot execute reliably, record the reason and switch to fallback. Python/MATLAB parity is created only when explicitly requested.

Every official run records the selected language, rationale, runtime, dependencies/toolboxes, entry point, source-tree snapshot, command, logs, inputs/outputs, assertions, and `official_run: true`. Formal results may reference only a successful official run.

## 7. Paper and LaTeX

The paper sequence is:

```text
verified results
  -> claim selection
  -> prose/equation/table/figure planning
  -> generate representations
  -> paper structure
  -> LaTeX writing
  -> rendered PDF QA
```

There is no minimum figure or page count. A figure-light plan raises a warning to reconsider communication, not a failure. The v0.5 scaffold uses broad narrative sections and allows restructuring instead of repeating a rigid analysis-assumption-model-solve template.

Final QA checks captions, tables, equations, page density, figure placement, fonts/glyphs, overflow, clipping, whitespace, and cross-page continuity. Internal IDs, evidence states, local paths, and workflow language remain blocking visible-text leaks; excessive precision and number-dense sentences are warnings.

The compile receipt binds the reviewed PDF to the exact editable LaTeX source-tree snapshot.

## 8. Start, check, and migrate

Initialize from a Codex conversation by supplying the official local path:

```text
Use $cumcm-workflow to initialize a CUMCM project from /absolute/path/to/2026B.
```

Maintainer interfaces:

```bash
python3 .agents/skills/cumcm-workflow/scripts/init_project.py \
  --project /path/to/new-project --project-id CUMCM-2026-B \
  --official /path/to/official-files

python3 .agents/skills/cumcm-workflow/scripts/cumcm_check.py \
  --project /path/to/project --stage validation \
  --profile strict --gate-mode enforce

python3 .agents/skills/cumcm-workflow/scripts/set_mode.py \
  --project /path/to/project --mode finalizing

python3 .agents/skills/cumcm-workflow/scripts/migrate_v04_to_v05.py \
  --source /path/to/v04-workspace --target /path/to/v05-workspace
```

Migration copies into a new target, never edits the v0.4 source, starts in working mode, and marks migrated runs non-official until one selected backend is rerun successfully.

For scoped revalidation, add `--changed <path>` and `--impact cosmetic|local|semantic|claim_changing|global`.

## 9. Hard invariants and provenance

The following remain blocking:

- official input mutation or identity mismatch;
- simulated data presented as observed;
- claim-bearing computation without a successful official run;
- code-source snapshot, formal input, or claim-bearing output drift;
- incorrect result locator or result/output mismatch;
- stale independent-review package or stage handoff;
- fabricated human approval or independent review;
- open validation/paper P0;
- unreadable or mismatched final PDF;
- final PDF not bound to approved QA and editable source;
- incomplete PDF/LaTeX/computation delivery roles.

Accepted decisions automatically create lightweight stage snapshots. Unchanged snapshots are trusted; a changed key artifact invalidates that stage and downstream trust. Hard invariants are still checked.

## 10. Repository and development

```text
.agents/skills/cumcm-workflow/
├── SKILL.md
├── references/
├── schemas/
├── scripts/
└── assets/
docs/
examples/
tests/
.github/workflows/ci.yml
```

Development validation:

```bash
python3 -m pip install -r requirements-ci.txt
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q .agents/skills/cumcm-workflow/scripts tests
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/cumcm-workflow
```

CI runs the exact dependency set on Python 3.10 and 3.13. Real paper releases still require XeLaTeX compilation and rendered-page inspection.

## 11. Limitations and license

Fresh context reduces contamination; it does not guarantee an independent or correct reviewer. Digests prove artifact identity, not mathematical validity. Backend selection is deterministic guidance, not a benchmark of every toolbox/package. Visual and semantic quality still require problem-specific judgment.

Historical designs remain in [v0.4 design](docs/v0.4-design.md) and [v0.3 design](docs/v0.3-design.md). The current design is [v0.5](docs/v0.5-design.md).

This repository is released under the [MIT License](LICENSE).
