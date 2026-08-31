# Reader-facing LaTeX paper template

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
- Add each quantitative figure through the figure manifest and record its stable result/claim link in `PAPER_TRACEABILITY.json`; never render that link in the paper.
- Keep the editable LaTeX reader-facing. Do not add `\evidence`, workflow-state, run-ID, or gate macros even when they are visually small.

## Format modes

The included `contest_ctex` template is designed for a clean CUMCM reading flow: no default table of contents, compact title and abstract transition, modular question sections, controlled formula spacing, and explicit mechanism-result-meaning placeholders. It remains submission-neutral and does not claim compliance with a particular year's package.

Use a high-quality reference paper to learn transferable hierarchy, whitespace, formula/table rhythm, and explanation order. Do not copy its problem-specific prose, figures, proprietary class, or fonts, and do not use its page count as a quality target.

Before delivery, compare the template only with current official rules supplied by the user, or adapt a user-supplied official package. Set `official_compliance` to `verified_against_current_rules` only after that actual review. Missing official material blocks delivery; it does not authorize web search.

Do not redistribute third-party document classes or fonts without a verified license. Prefer an adapter that consumes a user-supplied official package.

## Compilation and review

Compile with XeLaTeX. Preserve the selected argument array, engine version, logs, page count, warning scan, and final-PDF digest in `COMPILE_RECEIPT.json`. The quality report itself does not need a digest; its path and the reviewed PDF binding are sufficient. Render every final page, record the reviewed page set, and run the visible-text checker before final acceptance.
