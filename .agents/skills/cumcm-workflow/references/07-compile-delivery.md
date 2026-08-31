# Stage 7: Compile and delivery

Compile with the engine required by the selected template. Preserve the clean editable source, bibliography, required figures, computation source, compile log, and final PDF.

## User-supplied source boundary

Official compliance review uses only files or explicit source locations supplied by the user and recorded in `SOURCE_MANIFEST.json`. Do not search the web, cached pages, archives, or third-party repositories to fill missing rules or templates. If a required item is absent, set `source_policy.missing_user_materials`, report `blocked_missing_user_material`, and ask the user for it. A later explicit network authorization may collect an external reference, but it does not automatically become an official source.

## Required deliverables

The final user-facing delivery has three mandatory, separately addressable roles:

1. `final_pdf` — the exact reviewed PDF;
2. `editable_latex_source` — main file, sections, macros, bibliography, and required figures, compilable from the delivered copy;
3. `computation_source` — entry points, modules, and dependency instructions needed to rerun the solution when official data are supplied.

Missing any role blocks delivery. Do not replace editable source with a PDF-only archive.

Check:

- successful compilation and resolved references;
- anonymity and current competition formatting requirements;
- embedded fonts and missing glyphs;
- overflow, clipping, unreadable figures, and table layout;
- every delivered path and entry point against `DELIVERY_MANIFEST.json`;
- the final PDF digest; use the Git commit or source revision plus compile/rerun checks for ordinary source identity.

Record every meaningful compile attempt in `delivery/COMPILE_RECEIPT.json`. Use an argument array (`argv`), not only a shell command string. Select one successful attempt and bind its engine/version, exit code, log, diagnostics, warnings, page count, PDF path/hash, and font/glyph checks to the exact paper quality report and layout-reviewed PDF.

Keep the compact compile summary in `delivery/DELIVERY_MANIFEST.json` and set `compile_receipt_path`; the checker cross-checks the selected receipt against the summary, delivery PDF, paper quality report, layout page count, and LaTeX engine declared in the template manifest.

Before delivery, review the source against the current official competition rules and package. Record the exact source in `LATEX_TEMPLATE_MANIFEST.json`; the generic scaffold remains blocked until `official_compliance` is explicitly verified.

Hash only where byte identity materially changes the evidence: official sources, formal run inputs, claim-bearing outputs, stage-decision scope, and the exact reviewed final PDF. Ordinary LaTeX/code files, figures during editing, documentation, compile logs, caches, temporary files, and auxiliary files do not require SHA-256. An optional digest on those files is informational and stale values are warnings, not blockers.

In `strict`, render and inspect every final page. In `sprint`, prioritize high-risk pages but never label an incompletely reviewed artifact `final`. Record final `model-xray` audit as deferred unless explicitly requested. Submission remains a user-controlled action.
