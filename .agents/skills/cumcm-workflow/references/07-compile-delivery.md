# Stage 7: Compile and delivery

Compile with the engine required by the selected template. Preserve source, bibliography, figures, logs, and the final PDF.

Check:

- successful compilation and resolved references;
- anonymity and current competition formatting requirements;
- embedded fonts and missing glyphs;
- overflow, clipping, unreadable figures, and table layout;
- every delivered file against `DELIVERY_MANIFEST.json`;
- hashes of the final PDF, submission package, claim-bearing result files, and any separately delivered figures; use the Git commit or source revision for code identity when available.

Record the selected profile, exact compile command and engine, exit code, log, warnings, page count, final files and hashes, accepted exceptions, excluded sensitive files, and final human review in `delivery/DELIVERY_MANIFEST.json`.

Every file frozen in the delivery manifest has a blocking hash check. Byte-size drift is warning-only metadata because the digest comparison is authoritative. Do not hash compile logs, caches, temporary files, or LaTeX auxiliary files unless they are intentionally included in the submission package.

Render and inspect pages where formulas, dense tables, or figures may fail visually. Record final `model-xray` audit as deferred unless explicitly requested. Submission remains a user-controlled action.
