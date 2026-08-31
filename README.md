# CUMCM Codex Workflow

An evidence-bounded, reproducible, Codex-native workflow for the China Undergraduate Mathematical Contest in Modeling (CUMCM).

> Status: v0.4. This release accepts only v0.4 project contracts. A passing workflow is not proof that a model or paper is correct.

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

## Initialize from a Codex conversation

Put the official statement, attachments, and current rules in one directory when possible. In Codex, invoke the Skill and provide that path:

```text
请初始化国赛项目，官方题目和附件在 /absolute/path/to/2026B题。
```

Codex automatically selects `$cumcm-workflow`, inspects the path, infers the project ID, chooses a safe sibling workspace when you did not name one, and runs the initializer. You may name the Skill explicitly, but it is not required when the request is clear. Codex then reports the new absolute project path and the intake artifacts awaiting review. It asks only when the source is missing, the competition identifier cannot be inferred, or the target would overwrite existing work.

The underlying command remains available for maintainers and automation:

```bash
python3 .agents/skills/cumcm-workflow/scripts/init_project.py \
  --project /path/to/new-project \
  --project-id CUMCM-2026-B \
  --official /path/to/official-files
```

Initialization creates the complete v0.4 workspace, copies and inventories official inputs, writes state and machine-readable initialization/preflight reports, and stops at the intake review gate. It never infers problem facts, models, evidence, or approvals.

## Version 0.4

Version 0.4 provides:

- a user-routed independent-review package before validation, with a dedicated reviewer Skill and a hard prohibition on same-conversation self-approval;
- a paper plan with reference review, Claims-Evidence Matrix, reader narrative, per-question argument chains, and figure jobs;
- a contest-oriented modular CTeX scaffold with mechanism-first explanations and no default table of contents;
- separate content, layout, visible-text, and final-QA reviews bound to the exact reviewed PDF;
- a sidecar traceability contract that keeps internal IDs, evidence states, local paths, and gate vocabulary out of the final paper;
- quality-triggered revision snapshots and P0/P1/P2 issue tracking;
- a machine-readable compile receipt and a mandatory three-part delivery: final PDF, editable LaTeX source, and computation source;
- append-only, artifact-bound human decisions instead of silently editable approval fields;
- `preflight` and `enforce` gate modes, so automation can prepare a human review without weakening evidence failures;
- an official-material boundary: missing rules or templates must be requested from the user rather than filled by autonomous web search.

The seven workflow stages and the evidence chain from official facts through capabilities, models, runs, results, claims, figures, and delivery remain unchanged.

Final `model-xray` auditing remains an explicit, deferred hook rather than an automatic step.

SHA-256 is a narrow background identity mechanism, not a user-facing review ritual. It is required only for official sources, formal run inputs, claim-bearing outputs, approval scope, and the exact reviewed final PDF. Ordinary source files, editing-stage figures, logs, caches, documentation, and support files do not require a digest. Decision events are not hash-chained, and people review artifacts and summaries rather than digest strings.

See [docs/v0.4-design.md](docs/v0.4-design.md) for the complete design and [docs/workflow-contract.md](docs/workflow-contract.md) for stage gates. [docs/v0.3-design.md](docs/v0.3-design.md) is retained only as historical documentation.

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
