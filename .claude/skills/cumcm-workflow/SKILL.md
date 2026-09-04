---
name: cumcm-workflow
description: Build or resume a contest-ready CUMCM (China Undergraduate Mathematical Contest in Modeling) project from official problem files through modeling, one selected computation backend, bounded independent validation, fresh-context paper writing, and final delivery. Use for real CUMCM work; do not use for ordinary paper polishing or unsupported one-shot answers.
---

# CUMCM Workflow (Claude Code entry point)

This is a router. The workflow itself lives in one canonical tree so that the Codex and Claude Code entry points cannot drift apart:

```text
.agents/skills/cumcm-workflow/
├── SKILL.md      # the full workflow instructions -- read this first
├── references/   # per-stage guides
├── schemas/      # JSON Schemas for every machine-readable contract
├── scripts/      # the initializer, recorders, checker and handoff builders
└── assets/       # LaTeX scaffold and the independent-review package
```

## Do this

1. Read `.agents/skills/cumcm-workflow/SKILL.md` and follow it. Everything below is a summary of that file, not a substitute for it.
2. Read only the reference for the active stage, plus `references/handoffs.md` when crossing stages.
3. Run scripts as `python3 .agents/skills/cumcm-workflow/scripts/<name>.py ...` from the repository root. They resolve their own schemas and assets, so the working directory does not matter.

## The two rules that shape everything

- **Tooling records machine facts; you write judgement.** Never type a hash, an exit code, a page count, a source-tree digest or a result value. `record_run.py`, `index_result.py`, `record_compile.py` and `refresh_evidence.py` observe those.
- **The model is chosen late.** `working` mode accepts a draft model contract (method and scope only). The complete contract is frozen on entering `finalizing`.

## Common commands

```bash
S=.agents/skills/cumcm-workflow/scripts
python3 $S/init_project.py --project <new-dir> --project-id CUMCM-2026-B --official <official-files>
python3 $S/record_run.py --project <p> -- python3 code/try.py            # exploratory, zero declarations
python3 $S/record_run.py --project <p> --official --capability CAP-Q1-001 \
  --source code/solve.py --output results/q1.json:claim -- python3 code/solve.py
python3 $S/index_result.py --project <p> --result-id RES-Q1-001 --run RUN-Q1-001 \
  --locator results/q1.json#/minimum_cost --name "Minimum cost" --unit CNY --scope "..."
python3 $S/cumcm_check.py --project <p> --stage computation --gate-mode preflight
python3 $S/plan_redo.py --project <p> --changed code/solve.py
python3 $S/record_compile.py --project <p> --update-quality
```

## Boundaries

Never invent observed data, approvals, independent review, or successful execution. Never modify the copied official sources. Passing the checks establishes structure, provenance and preserved execution — never mathematical correctness.

To use this outside a checkout, copy this directory to `~/.claude/skills/cumcm-workflow/` and keep the repository available; the router's relative paths assume the repository is the working root.
