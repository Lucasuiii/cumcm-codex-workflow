# Stage 6: Paper writing

## Inputs

Use only approved problem facts, the model contract, indexed executed results, validated claims, and figures registered in `figures/FIGURE_MANIFEST.json`.

Create and maintain:

- `paper/PAPER_PLAN.json` before drafting;
- `paper/LATEX_TEMPLATE_MANIFEST.json` by following [latex-template.md](latex-template.md);
- `paper/PAPER_QUALITY_REPORT.json` during content and layout review;
- `paper/PAPER_REVISION_LOG.json` from the first stable draft onward.
- `paper/PAPER_TRACEABILITY.json` for internal claim/result links that must not render;
- `paper/PAPER_VISIBLE_TEXT_REPORT.json` from the final rendered PDF.

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

Also write a reader narrative: one sentence stating the paper's contribution, the judge's intended reading path, and `internal_metadata_policy: sidecar_only`. The traceability layer and the reader-facing paper are separate products. Keep all stable IDs, evidence states, run coverage, local paths, and gate vocabulary in JSON sidecars. Do not define a LaTeX macro that renders them.

Plan figures by explanatory job. A quantitative figure must identify both the claim it helps explain and the indexed result it visualizes. Reconcile required planned figures with `FIGURE_MANIFEST.json`; do not generate figures merely to meet a count.

## Rules

- Write the abstract after the body and validation are stable.
- Trace every important number to a result ID and every high-bearing statement to a claim ID.
- Store that mapping only in `PAPER_TRACEABILITY.json`; the clean LaTeX and PDF use natural language.
- Distinguish fact, assumption, method, result, and limitation.
- Do not create new numerical results while writing.
- Do not impose a minimum page count or repeat material to create volume.
- Include only figures that explain data, model behavior, comparison, validation, sensitivity, or decisions.
- Mark conceptual figures explicitly; they must not visually imply measured quantities. Record every quantitative figure's result IDs, run IDs, transformations, axes, units, caption claims, and visual review. A figure digest is optional.
- Treat an optional figure hash mismatch during editing as a stale-manifest warning: inspect the change and refresh or remove the optional digest when the figure is accepted. Delivery does not require per-figure hashes; the reviewed final PDF is the frozen reader-facing artifact.
- Verify citations from real sources; do not fabricate bibliographic entries.
- Write each subproblem as a problem-solving story: task and difficulty, mechanism, model, solution, result, meaning, validation, and boundary. Equations need purpose before them and interpretation after them.
- Prefer a representative result plus meaning over lists of intermediate values. Use precision justified by measurement, uncertainty, or decision needs; flag rather than blindly preserve machine precision.
- Write the abstract last. Give each subproblem its own compact method-result-meaning paragraph. The conclusion answers the questions directly and moves diagnostics to the body.
- Treat figures as evidence in the argument, not as the grammatical subject of repetitive “Figure X shows” paragraphs. Define reader-facing terms at first use.

## Review and revise

Bind every review to the exact paper path and SHA-256. Perform content review separately from layout review:

- Content review checks each subproblem's argument chain, mechanism explanation, derivation, result interpretation, reader-facing language, numerical presentation, validation strength, and limitations. It separately reviews abstract synthesis, conclusion directness, reference-style transfer, and internal-metadata separation.
- Layout review renders the PDF and checks hierarchy, equations, tables, figures, captions, whitespace, pagination, fonts/glyphs, and cross-page continuity. In `strict` mode, record every reviewed page.

Classify issues as `P0`, `P1`, or `P2`. A final paper cannot retain an open `P0`. Iterate until the issue evidence supports closure; do not require a fixed number of rounds. Each revision records version-bound input/output snapshots, issue IDs, changed locations, and verification. If time expires with unresolved critical work, report `technical_draft` rather than calling it final.

Run `scripts/paper_visible_text_check.py` on the reviewed PDF. Internal IDs, evidence-state enum values, workflow gate language, and local paths are blocking. Excessive decimal precision and number-dense sentences are review flags: revise them or record a specific reader-facing reason for retention. The final report must be accepted and bound to the same PDF as `PAPER_QUALITY_REPORT.json`.

The same conversation may prepare a candidate and self-review notes, but it cannot alone set reader-facing content or final QA to final. A human user or separately identified reviewer must accept the exact PDF. A later `revision_requested` decision supersedes an earlier acceptance and reopens paper work.

Use preflight to prepare the review, show the exact artifacts and open issues, and stop for the user's decision before recording acceptance or final compilation.
