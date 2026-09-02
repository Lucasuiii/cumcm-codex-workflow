# Paper responsibility

Start in a fresh task when practical. Read `handoffs/validation-paper/HANDOFF.json` first; open upstream files only through its canonical pointers. Do not load failed runs, debug logs, or old review conversations unless a current P0 specifically requires them.

## Claim-led sequence

1. select the validated claims that answer the official questions;
2. choose the best representation for each claim: prose, equation, table, or figure;
3. generate the required tables/figures from indexed results;
4. design a paper structure that covers every subproblem without forcing a stock section template;
5. initialize or adapt LaTeX;
6. compile, render, and review the PDF.

`PAPER_PLAN.json` therefore requires only `claim_selection`, `representation_plan`, and `paper_structure`. Legacy nine-layer plans, reference-paper counts, page budgets, and figure counts may remain as optional notes but are not hard gates. A plan with no table/figure creates a warning to reconsider communication, not a failure.

## Reader-facing quality

- Explain why equations and algorithms are used and what results mean.
- Prefer a representative result plus interpretation over number dumping.
- Use tables for exact comparisons, figures for patterns/relationships, equations for mechanisms, and prose for conclusions or assumptions.
- Give captions enough context to understand the claim, scope, axes/units, and comparison without repeating the body.
- Keep internal IDs, evidence states, local paths, workflow terms, and run coverage in sidecars only.
- Do not create new numerical results while writing.
- Do not impose a minimum page or chart count.

`PAPER_QUALITY_REPORT.json` binds content, rendered layout, and final QA to the exact PDF. Open P0 issues block final status. P1 concerns and P2 suggestions remain visible but do not block. Failed layout checks that make equations, tables, figures, glyphs, or pages unreadable remain hard submission-reliability failures.

Run `paper_visible_text_check.py`. Internal metadata and local paths block; excessive decimal precision and number-dense sentences are warnings for reader review. A revision log is optional: use it when it helps track a real P0/P1 correction, not to force rounds.

Build `paper-delivery` after the exact PDF and editable source are approved.
