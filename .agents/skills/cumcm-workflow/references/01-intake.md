# Stage 1: Intake

## Goal

Create a read-only inventory of the official problem, attachments, and current competition rules before interpretation.

## Procedure

1. Copy inputs into `problem/` without altering originals.
2. Run `inventory_artifacts.py` to create `SOURCE_MANIFEST.json` with relative paths, sizes, and SHA-256 hashes.
3. Record provenance as `official`, `user-provided`, or `derived`.
4. Render PDFs when formulas, tables, or layout carry meaning. Use extracted text only for navigation.
5. Initialize `.cumcm/state.json` with `intake: passed` only after every expected official attachment is accounted for.

Do not run code or macros embedded in unfamiliar inputs during intake.
