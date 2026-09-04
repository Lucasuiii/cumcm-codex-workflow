# Reader-facing LaTeX scaffold

Initialize after a claim-led `PAPER_PLAN.json` exists:

```bash
python3 scripts/init_latex_paper.py --project <project> --competition-year <year> \
  --title <title> --keywords '<actual object; model; method>'
```

Supply `--title` and `--keywords` from the actual problem, model, data, or method. The initializer has no reader-facing generic fallback and rejects generic title placeholders or workflow-oriented keyword filler.

The initializer checks exact subproblem coverage through `paper_structure`, stages all generated files, and publishes them transactionally with rollback if a commit fails. It refuses to overwrite existing source. If source metadata declares an adaptable official paper template, generic initialization stops so that template can be adopted or adapted. Format/submission/competition instructions do not block generic initialization; they remain bound official materials and `official_compliance` stays `unverified` until paper/delivery checks them. Filename keywords alone do not decide the role.

The scaffold keeps setup in `main.tex`, metadata in `metadata.tex`, shared notation/macros in `macros.tex`, and substantive writing in `sections/`. Abstract, references, and appendix are generic outer modules. Every body section and its input order come directly from `PAPER_PLAN.paper_structure`; the initializer does not generate per-question subsection trees or a LaTeX AST. Purpose, covered-subproblem IDs, and claim IDs appear only as comments for the writer and never render.

Remove placeholder markers before final status. Add only figures/tables selected for a real claim. Keep internal IDs out of rendered text; `paper_visible_text_check.py` measures that on the PDF. The generic scaffold is submission-neutral; adapt a user-supplied official package when required.

The generic style uses restrained heading/equation/float spacing, booktabs-friendly tables, `tabularx`/`longtable`, and subfigure support. Do not shrink dense tables reflexively or force floats away from their argument. Compile with `record_compile.py`. It runs the declared engine, writes `COMPILE_RECEIPT.json` with the PDF hash and a `sha256-tree-v1` snapshot of every required source file, reads the page count out of the PDF, rasterises every page to `.cumcm/tmp/pages/`, and derives the layout checks (overfull boxes, undefined references, missing glyphs, font errors) from the engine log:

```bash
python3 scripts/record_compile.py --project <p> --update-quality
```

With `--update-quality` it refreshes the machine fields of `PAPER_QUALITY_REPORT.layout_review` — page count, rendered pages, checks, bound artifact — and leaves the decision to you. Then actually look at the rendered pages: equations, tables, captions, figure placement, page density, whitespace, fonts and cross-page continuity are human QA, not a machine score.
