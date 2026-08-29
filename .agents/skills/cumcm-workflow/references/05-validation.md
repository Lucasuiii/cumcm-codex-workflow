# Stage 5: Validation

## Required outputs

- `validation/VALIDATION_REPORT.md`
- `validation/CLAIM_LEDGER.json`
- `validation/SENSITIVITY_REPORT.md` when sensitivity is relevant

Recompute important checks from saved outputs rather than trusting in-process variables or solver success flags. Test units, bounds, conservation, feasibility, baseline comparisons, and cross-subproblem consistency.

For every proposed paper claim, record:

- the exact claim;
- its scope and assumptions;
- supporting run and output paths;
- independent or structural checks;
- known confounds and limitations;
- status: `supported`, `partially_supported`, `contradicted`, `missing_evidence`, or `ambiguous`.

Stop for approval of claims that may enter the abstract or conclusion.
