# Evidence rules

## Evidence strength

- File existence proves delivery only.
- Schema validity proves structure only.
- Keyword presence proves neither implementation nor correctness.
- An executed command proves that the recorded process ran, not that it implemented the model.
- A result link proves traceability only when the indexed value matches the executed output locator.
- A successful solver status does not prove the formulation matches the problem.
- A heuristic result does not prove global optimality.
- Non-rejection in a statistical test does not prove equivalence.
- A sensitivity curve is evidence only when values come from executed runs.

## Strong claims

Claims of global optimality, unbiasedness, equivalence, causality, statistical significance, robustness, or reproducibility require claim-specific evidence, an explicit scope, and the relevant certificate. A restricted-class optimum must name the class. Non-rejection is not equivalence. A successful original run is not reproduction.

## Profiles

`strict` and `sprint` differ in exploratory breadth and polish. Neither profile may demote official-source hashes, formal run input or claim-bearing output hashes, the exact reviewed final-PDF hash, execution, contradiction, cross-question consistency, result trace, or claim-evidence errors. Editing-stage figure hash drift, optional support-file hash drift, and redundant byte-size mismatches are warnings in both profiles. Sprint may defer alternative-model comparison and nonessential figures only when the corresponding strong claim is also removed or narrowed.

## Conflict handling

When the statement, code, results, figures, and paper disagree, preserve every version, identify the authoritative source for that field, mark the claim unresolved, and return to the earliest stage that introduced the conflict.

Dependent stages become blocked, but their artifacts remain available for comparison and localized rebuilding.
