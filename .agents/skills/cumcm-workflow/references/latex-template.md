# LaTeX paper scaffold

Read this reference after `PAPER_PLAN.json` exists and before drafting paper sections.

Initialize the canonical modular scaffold:

```bash
python3 scripts/init_latex_paper.py --project <project> --competition-year <year> --title <title>
```

The initializer reads `.cumcm/state.json`, `analysis/PROBLEM_FACTS.json`, and `paper/PAPER_PLAN.json`. It requires exact subproblem coverage, creates one section file per subproblem, writes `paper/LATEX_TEMPLATE_MANIFEST.json`, and refuses to overwrite existing paper sources.

## Editing boundary

- Keep document setup and section assembly in `paper/main.tex`.
- Keep title, year, and keywords in `paper/metadata.tex`.
- Keep shared notation in `paper/macros.tex`.
- Write substantive content only in `paper/sections/*.tex` unless a verified official package requires another structure.
- Remove `CUMCM-TODO` and `\placeholder{...}` markers only after replacing them with evidence-backed content. Final status is blocked while any marker remains.
- Add each quantitative figure through the figure manifest and a stable result/claim link; do not paste unregistered numbers into the paper.

## Format modes

The included `generic_ctex` scaffold is for reliable local drafting and compilation. It does not claim compliance with a particular year's submission package. Before delivery, compare it with the current official rules or adapt the current official package, record its source, and set `official_compliance` to `verified_against_current_rules` only after an actual review.

Do not redistribute third-party document classes or fonts without a verified license. Prefer an adapter that consumes a user-supplied official package.

## Compilation and review

Compile with XeLaTeX. Preserve the selected command, engine version, logs, page count, warning scan, and PDF binding in `COMPILE_RECEIPT.json`. Render every page of a final PDF and record the reviewed page set in `PAPER_QUALITY_REPORT.json`.
