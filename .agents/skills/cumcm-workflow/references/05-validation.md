# Stage 5: Validation

## Entry gate: user-routed independent review

Validation may not begin immediately after computation. First run `scripts/build_independent_review_package.py --project <project>`. It creates `validation/independent-review-package/` containing official inputs, problem and model contracts, computation entry points, run records, executed outputs, a review request, and a dedicated reviewer `SKILL.md`. The package withholds the originating conclusions as far as practical.

Stop after packaging. Show the package to the user and let the user choose a human or model in a separate task. Record the choice in `REVIEW_PACKAGE_MANIFEST.json`; never default to the current conversation. Import the raw review as `validation/INDEPENDENT_REVIEW_RAW.md` and the structured result as `validation/INDEPENDENT_REVIEW_RESULT.json`.

A same-context review is `correlated_self_review` and cannot pass. A same-model fresh task may pass only as `context_separated_model_correlated`; preserve that limitation. A different model or human can be marked `independent`, but the result is still a review, not mathematical proof. A `revision_requested` verdict returns to the earliest affected stage. An inconclusive review blocks validation until the missing user-supplied material or evidence is resolved.

## Required outputs

- `validation/VALIDATION_REPORT.md`
- `validation/CLAIM_LEDGER.json`
- `validation/independent-review-package/REVIEW_PACKAGE_MANIFEST.json`
- `validation/INDEPENDENT_REVIEW_RAW.md`
- `validation/INDEPENDENT_REVIEW_RESULT.json`
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

Stop for approval of claims that may enter the abstract or conclusion.
