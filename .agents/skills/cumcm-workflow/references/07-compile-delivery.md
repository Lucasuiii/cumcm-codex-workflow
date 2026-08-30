# Stage 7: Compile and delivery

Compile with the engine required by the selected template. Preserve source, bibliography, figures, logs, and the final PDF.

Check:

- successful compilation and resolved references;
- anonymity and current competition formatting requirements;
- embedded fonts and missing glyphs;
- overflow, clipping, unreadable figures, and table layout;
- every delivered file against `DELIVERY_MANIFEST.json`;
- hashes of the final PDF, submission package, claim-bearing result files, and any separately delivered figures; use the Git commit or source revision for code identity when available.

Record every meaningful compile attempt in `delivery/COMPILE_RECEIPT.json`. Use an argument array (`argv`), not only a shell command string. Select one successful attempt and bind its engine/version, exit code, log, diagnostics, warnings, page count, PDF path/hash, and font/glyph checks to the exact paper quality report and layout-reviewed PDF.

Keep the compact compile summary in `delivery/DELIVERY_MANIFEST.json` and set `compile_receipt_path`; the checker cross-checks the selected receipt against the summary, delivery PDF, paper quality report, layout page count, and LaTeX engine declared in the template manifest.

Before delivery, review the source against the current official competition rules and package. Record the exact source in `LATEX_TEMPLATE_MANIFEST.json`; the generic scaffold remains blocked until `official_compliance` is explicitly verified.

Every file frozen in the delivery manifest has a blocking hash check. Byte-size drift is warning-only metadata because the digest comparison is authoritative. Do not hash compile logs, caches, temporary files, or LaTeX auxiliary files unless they are intentionally included in the submission package.

In `strict`, render and inspect every final page. In `sprint`, prioritize high-risk pages but never label an incompletely reviewed artifact `final`. Record final `model-xray` audit as deferred unless explicitly requested. Submission remains a user-controlled action.
