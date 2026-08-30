# Stage 6: Paper writing

## Inputs

Use only approved problem facts, the model contract, indexed executed results, validated claims, and figures registered in `figures/FIGURE_MANIFEST.json`.

Create and maintain:

- `paper/PAPER_PLAN.json` before drafting;
- `paper/LATEX_TEMPLATE_MANIFEST.json` by following [latex-template.md](latex-template.md);
- `paper/PAPER_QUALITY_REPORT.json` during content and layout review;
- `paper/PAPER_REVISION_LOG.json` from the first stable draft onward.

## Plan before drafting

Review at least one genuinely useful high-quality reference in `strict` mode. Record why it is useful, which lessons transfer, and which features do not transfer to this problem. Do not imitate surface length or chart density.

Build a Claims-Evidence Matrix connecting each validated claim to the section and stable evidence IDs that will support it. For every subproblem, plan all nine parts of the argument chain:

1. problem interpretation;
2. assumptions and boundaries;
3. variables and parameters;
4. objective and constraints;
5. derivation;
6. algorithm or solution procedure;
7. results;
8. validation;
9. limitations.

Use `not_applicable` only with a concrete rationale. An included part needs evidence IDs. A page budget is a planning aid, not a pass condition.

Plan figures by explanatory job. A quantitative figure must identify both the claim it helps explain and the indexed result it visualizes. Reconcile required planned figures with `FIGURE_MANIFEST.json`; do not generate figures merely to meet a count.

## Rules

- Write the abstract after the body and validation are stable.
- Trace every important number to a result ID and every high-bearing statement to a claim ID.
- Distinguish fact, assumption, method, result, and limitation.
- Do not create new numerical results while writing.
- Do not impose a minimum page count or repeat material to create volume.
- Include only figures that explain data, model behavior, comparison, validation, sensitivity, or decisions.
- Mark conceptual figures explicitly; they must not visually imply measured quantities. Record every quantitative figure's result IDs, run IDs, transformations, axes, units, hash, caption claims, and visual review.
- Treat a figure hash mismatch during editing as a stale-manifest warning: inspect the change and refresh the manifest when the figure is accepted. Freeze final figure hashes through the delivery manifest.
- Verify citations from real sources; do not fabricate bibliographic entries.

## Review and revise

Bind every review to the exact paper path and SHA-256. Perform content review separately from layout review:

- Content review checks each subproblem's argument chain, derivation, result interpretation, validation strength, and limitations.
- Layout review renders the PDF and checks hierarchy, equations, tables, figures, captions, whitespace, pagination, fonts/glyphs, and cross-page continuity. In `strict` mode, record every reviewed page.

Classify issues as `P0`, `P1`, or `P2`. A final paper cannot retain an open `P0`. Iterate until the issue evidence supports closure; do not require a fixed number of rounds. Each revision records version-bound input/output snapshots, issue IDs, changed locations, and verification. If time expires with unresolved critical work, report `technical_draft` rather than calling it final.

Use preflight to prepare the review, show the exact artifacts and open issues, and stop for the user's decision before recording acceptance or final compilation.
