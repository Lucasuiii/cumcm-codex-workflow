# Stage 5: Validation

## Required outputs

- `validation/VALIDATION_REPORT.md`
- `validation/CLAIM_LEDGER.json`
- `.cumcm/validation-report.json`
- `validation/SENSITIVITY_REPORT.md` when sensitivity is relevant

Recompute important checks from saved outputs rather than trusting in-process variables or solver success flags. Test units, bounds, conservation, feasibility, baseline comparisons, and cross-subproblem consistency.

For every proposed paper claim, record:

- the exact claim;
- its scope and assumptions;
- supporting fact, model, run, result, and figure IDs;
- independent or structural checks;
- known confounds and limitations;
- evidence state: `not_checked`, `missing_evidence`, `supported_not_reproduced`, `reproduced`, `partially_supported`, `contradicted`, `ambiguous`, or `not_applicable`.

Claims of global optimality, unbiasedness, equivalence, causality, or robustness require a claim-specific certificate declaration. `reproduced` additionally requires an isolated rerun and a claim-specific comparison record; stored code or a successful original run is insufficient.

Perform a separate logic-review pass with the conclusions withheld as far as practical. A fresh Codex task, a different model, or a human may perform it, but same-model review remains correlated and must not be described as independent proof.

Stop for approval of claims that may enter the abstract or conclusion.
