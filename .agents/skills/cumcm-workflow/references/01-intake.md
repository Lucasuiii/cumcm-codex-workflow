# Stage 1: Intake

## Goal

Create a read-only inventory of the official problem, attachments, and current competition rules before interpretation.

## Procedure

1. Copy inputs into `problem/official/` without altering originals.
2. Run `inventory_artifacts.py` with `--project-root` and `--project-id` to create `problem/SOURCE_MANIFEST.json` with stable source IDs, relative paths, sizes, SHA-256 hashes, and origin.
3. Classify origin as `official`, `organizer_attachment`, `external_reference`, or `team_created`. Record derived files separately with their parent source ID.
4. Render PDFs when formulas, tables, or layout carry meaning. Use extracted text only for navigation.
5. Initialize `.cumcm/state.json` with exact workflow version `0.3.0`. Set `intake: passed` only after every expected official attachment is accounted for, preflight passes, and the artifact-bound decision is recorded.

Run `cumcm_check.py --stage intake --gate-mode preflight`, obtain the human decision, record it, then run `--gate-mode enforce`. Passing proves source identity and the declared inventory, not that the expected-source list is complete; a human must confirm that list.

Let the inventory and validator record and compare SHA-256 automatically. The reviewer confirms the source list and origin, not the digest characters. A hash mismatch blocks intake; a byte-size mismatch is only stale metadata and should be refreshed.

Do not run code or macros embedded in unfamiliar inputs during intake.
