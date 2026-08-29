# Stage 1: Intake

## Goal

Create a read-only inventory of the official problem, attachments, and current competition rules before interpretation.

## Procedure

1. Copy inputs into `problem/official/` without altering originals.
2. Run `inventory_artifacts.py` with `--project-root` and `--project-id` to create `problem/SOURCE_MANIFEST.json` with stable source IDs, relative paths, sizes, SHA-256 hashes, and origin.
3. Classify origin as `official`, `organizer_attachment`, `external_reference`, or `team_created`. Record derived files separately with their parent source ID.
4. Render PDFs when formulas, tables, or layout carry meaning. Use extracted text only for navigation.
5. Initialize the v0.2 `.cumcm/state.json`. Set `intake: passed` only after every expected official attachment is accounted for and the manifest review is accepted.

Run `cumcm_check.py --stage intake`. Passing proves source identity and the declared inventory, not that the expected-source list is complete; a human must confirm that list.

Do not run code or macros embedded in unfamiliar inputs during intake.
