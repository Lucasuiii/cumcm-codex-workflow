# Reader-facing LaTeX scaffold

Initialize after a claim-led `PAPER_PLAN.json` exists:

```bash
python3 scripts/init_latex_paper.py --project <project> --competition-year <year> --title <title>
```

The initializer checks exact subproblem coverage through `paper_structure`, stages all generated files, and publishes them transactionally with rollback if a commit fails. It refuses to overwrite existing source.

The v0.5 scaffold keeps setup in `main.tex`, metadata in `metadata.tex`, notation in `macros.tex`, and substantive writing in `sections/`. Its default question section uses three broad narrative units—task/mechanism/route; model/derivation/solution; results/validation/boundary—and explicitly allows restructuring. It avoids repeating a rigid analysis-assumption-model-solve template for every question.

Remove placeholder markers before final status. Add only figures/tables selected for a real claim. Keep traceability sidecar-only. The generic scaffold is submission-neutral; adapt a user-supplied official package when required.

Compile with the declared engine, render every final page, and inspect equations, tables, captions, figure placement, page density, whitespace, fonts/glyphs, and cross-page continuity. The compile receipt must snapshot every required source file and bind that source tree to the reviewed PDF.
