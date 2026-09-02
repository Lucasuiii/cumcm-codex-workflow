# Reader-facing LaTeX scaffold

Initialize after a claim-led `PAPER_PLAN.json` exists:

```bash
python3 scripts/init_latex_paper.py --project <project> --competition-year <year> \
  --title <title> --keywords '<actual object; model; method>'
```

Supply `--title` and `--keywords` from the actual problem, model, data, or method. The initializer has no reader-facing generic fallback and rejects generic title placeholders or workflow-oriented keyword filler.

The initializer checks exact subproblem coverage through `paper_structure`, stages all generated files, and publishes them transactionally with rollback if a commit fails. It refuses to overwrite existing source. If source metadata declares an adaptable official paper template, generic initialization stops so that template can be adopted or adapted. Format/submission/competition instructions do not block generic initialization; they remain bound official materials and `official_compliance` stays `unverified` until paper/delivery checks them. Filename keywords alone do not decide the role.

The scaffold keeps setup in `main.tex`, metadata in `metadata.tex`, shared notation/macros in `macros.tex`, and substantive writing in `sections/`. Abstract, references, and appendix are generic outer modules. Every body section and its input order come directly from `PAPER_PLAN.paper_structure`; the initializer does not generate per-question subsection trees or a LaTeX AST. Purpose, covered-subproblem IDs, and claim IDs appear only as comments for the writer and never render.

Remove placeholder markers before final status. Add only figures/tables selected for a real claim. Keep traceability sidecar-only. The generic scaffold is submission-neutral; adapt a user-supplied official package when required.

The generic style uses restrained heading/equation/float spacing, booktabs-friendly tables, `tabularx`/`longtable`, and subfigure support. Do not shrink dense tables reflexively or force floats away from their argument. Compile with the declared engine, render every final page, and inspect equations, tables, captions, figure placement, page density, whitespace, fonts/glyphs, and cross-page continuity. Visual aesthetics remain human QA, not a machine score. The compile receipt must snapshot every required source file and bind that source tree to the reviewed PDF.
