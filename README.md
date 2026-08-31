# CUMCM Codex Workflow

English | [简体中文](README.zh-CN.md)

An evidence-bounded, reproducible, Codex-native workflow for the China Undergraduate Mathematical Contest in Modeling (CUMCM).

> Current release: **v0.4**. This Skill accepts only v0.4 project contracts. Passing its checks proves workflow consistency, not that a mathematical model or paper is correct.

## What v0.4 is designed to do

- Start a complete contest workspace from user-supplied official files in one Codex conversation.
- Keep official sources, modeling decisions, executed computation, claims, figures, and delivery artifacts traceable.
- Stop at explicit human gates instead of silently choosing consequential interpretations or approving its own work.
- Route computation through a separate, user-selected review task before validation.
- Produce a judge-facing LaTeX/PDF paper while keeping internal IDs, evidence states, local paths, and workflow language in sidecar files.
- Deliver the reviewed PDF, editable LaTeX source, and computation source as three distinct outputs.
- Resume from files on disk rather than depending on chat history.

## Workflow

```text
official files
     |
     v
intake -> problem analysis -> model design -> computation
                                                   |
                                                   v
                                      independent review package
                                                   |
                                      user routes it to a separate reviewer
                                                   |
                                                   v
validation -> paper -> delivery -> optional user-requested final audit
```

The seven project stages remain `intake`, `problem-analysis`, `model-design`, `computation`, `validation`, `paper`, and `delivery`. Independent review is a blocking gate between computation and validation, not an eighth self-approved stage.

| Stage | Main outcome | Human gate |
|---|---|---|
| Intake | official inputs, source inventory, and project state | confirm that the official input set is complete |
| Problem analysis | facts, interpretation, assumptions, and required capabilities | approve the problem interpretation and coverage |
| Model design | model contract, alternatives, dependencies, and claim scope | choose the model and its declared limits |
| Computation | runnable code, preserved runs, logs, and indexed results | approve the executed evidence entering review |
| Independent review gate | conclusion-withheld package plus a structured review result | user selects a separate human or model reviewer; same-conversation approval is rejected |
| Validation | evidence states, consistency checks, limitations, and claim ledger | approve what the evidence actually supports |
| Paper | modular LaTeX, traceability sidecars, content/layout/visible-text QA | approve the exact reviewed manuscript and close critical issues |
| Delivery | compile receipt, final PDF, editable LaTeX, computation source, and manifest | confirm official-format compliance and the final package |

Conflicts return to the earliest stage that owns them. Downstream files are preserved, but dependent stages cannot pass until the conflict is resolved and reviewed again.

## Start from a Codex conversation

Open this repository as a Codex project, keep the official statement, attachments, and current rules accessible locally, then give Codex their path:

```text
Use $cumcm-workflow to initialize a CUMCM project. The official problem and attachments are at /absolute/path/to/2026B.
```

The explicit `$cumcm-workflow` name is optional when the request clearly concerns a CUMCM project. Codex will:

1. inspect only the supplied file or directory;
2. infer a stable project ID such as `CUMCM-2026-B`;
3. choose a safe sibling workspace unless a target is supplied;
4. run the initializer with absolute paths;
5. report the created workspace and stop at the intake review gate.

It asks for clarification only when the source is missing, the year/problem identifier remains ambiguous, or the target would overwrite existing work. Initialization copies but never edits or deletes the official source files. It does not invent facts, models, results, reviews, or approvals.

Maintainers and automation may call the underlying initializer directly:

```bash
python3 .agents/skills/cumcm-workflow/scripts/init_project.py \
  --project /path/to/new-project \
  --project-id CUMCM-2026-B \
  --official /path/to/official-files
```

## Independent review before validation

After computation, the Skill builds `validation/independent-review-package/`. The package contains the necessary official inputs, problem and model contracts, computation entry points, run records, executed outputs, a review request, and a dedicated reviewer Skill. The originating task stops and asks the user to route this package to a separate task or human reviewer.

The raw review is preserved verbatim, while `INDEPENDENT_REVIEW_RESULT.json` records reviewer identity, scope, findings, and verdict. A review performed in the originating conversation cannot pass the gate. A fresh task using the same model is marked as correlated rather than fully independent. Review acceptance is evidence, not mathematical proof.

## Reader-facing paper and delivery

The bundled `cumcm-contest-ctex` scaffold is modular and question-driven. It does not add a table of contents by default. Each question is expected to explain the task interpretation, mechanism, model, algorithm, results, validation, and limitations as a coherent argument.

Internal traceability stays in `PAPER_TRACEABILITY.json` and related sidecars. The visible-text check blocks internal IDs, evidence-state enums, local paths, and workflow gate language from leaking into the final PDF. Excessive decimal precision and number-dense sentences require revision or an explicit reader-facing justification.

Delivery requires three separately addressable roles:

1. the exact reviewed final PDF;
2. editable LaTeX source, including its entry point and required assets;
3. computation source, including its entry point and rerun instructions.

The scaffold is submission-neutral. Final compliance must be checked against current official rules or templates supplied by the user. Missing official material blocks delivery; it does not authorize autonomous web search or submission.

## Validation and gate modes

From the repository root:

```bash
python3 .agents/skills/cumcm-workflow/scripts/cumcm_check.py \
  --project /path/to/project \
  --stage validation \
  --profile strict \
  --gate-mode enforce
```

The report is written to `.cumcm/validation-report.json`.

- `strict` is the default. `sprint` may reduce exploration and polish, but never source, execution, consistency, evidence, or delivery checks.
- `preflight` distinguishes “automation complete, waiting for a person” from a failed build. It may return zero with `gate_status=awaiting_review` only when every remaining finding is a human decision.
- `enforce` is required before a stage is treated as passed.

Neither mode certifies mathematical correctness, statistical validity, or global optimality.

## Narrow SHA-256 policy

SHA-256 is a background identity mechanism only where byte-for-byte identity matters:

- user-supplied official sources;
- formal computation inputs and claim-bearing outputs;
- the small set of stage contracts covered by an explicit approval;
- the exact final PDF reviewed for paper QA and delivery.

Ordinary code, LaTeX, documentation, editing-stage figures, logs, caches, temporary files, and support files do not require digests. Decision events are append-only but are not hash-chained. Reviewers approve artifacts and summaries, not 64-character hash strings.

## Repository layout

```text
.agents/skills/cumcm-workflow/
├── SKILL.md                 # workflow router and invariants
├── agents/openai.yaml       # Codex UI metadata and invocation policy
├── references/              # stage guides and evidence contracts
├── schemas/                 # v0.4 machine-readable contracts
├── scripts/                 # initializer, validators, packaging, and paper checks
└── assets/
    ├── independent-review/  # reviewer Skill and request template
    └── latex-template/      # modular CTeX paper scaffold
docs/                        # architecture, workflow contract, and v0.4 design
examples/                    # regression contracts without official contest assets
tests/                       # contract and behavior tests
```

No official contest problems, private trial artifacts, generated workspaces, or submission files belong in this repository.

## Development validation

Requirements: Python 3.10+ and `jsonschema>=4.18`.

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  .agents/skills/cumcm-workflow
```

The second command uses the bundled Codex validator when available. Real paper releases still require XeLaTeX compilation and rendered-page visual review; a passing unit test is not visual QA.

## Documentation

- [v0.4 design](docs/v0.4-design.md)
- [workflow contract](docs/workflow-contract.md)
- [architecture](docs/architecture.md)
- [limitations](docs/limitations.md)
- [provenance](docs/provenance.md)
- [v0.3 historical design](docs/v0.3-design.md)

Final `model-xray` auditing remains an optional, user-invoked hook rather than an automatic stage.

## Safety and licensing

- Never invent empirical data to make a preferred method look better.
- Never call an approximate or restricted-class result globally optimal without a certificate and declared scope.
- Never write paper claims that are not traceable to executed outputs.
- Never treat schemas, keyword checks, solver success flags, or reviewer acceptance as proof of mathematical correctness.

This repository is independently designed and authored for reproducible CUMCM work. It is released under the [MIT License](LICENSE).
