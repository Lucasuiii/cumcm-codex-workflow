# Validation responsibility

## First review: full and context-separated

Build the current computation handoff, then run:

```bash
python3 scripts/build_independent_review_package.py --project <project>
```

The package binds official inputs, model contracts, selected source, official runs, and executed outputs with file hashes, an upstream digest, and a package digest. Stop and let the user route it to a separate task or human. Record both originating and reviewer task references; they must differ. Same-model fresh-context review remains correlated. Task references and user confirmation improve context-separation evidence but cannot cryptographically prove reviewer independence.

## Findings and verdicts

- `P0`: actual data/computation error, task mismatch, unsupported key claim, code/model/result disagreement, or serious provenance failure.
- `P1`: concern about model choice, assumptions, baseline, validation, sensitivity, or generalization.
- `P2`: optional presentation or additional experiment suggestion.

Verdicts are `accepted`, `accepted_with_concerns`, `revision_required`, and `inconclusive`. Only an open P0 permits `revision_required`. Open P1/P2 items remain visible as warnings or suggestions and do not block paper work.

After a full review returns open P0 findings, rerunning the package builder in auto mode defaults to a targeted re-review. It archives the prior review/package and targets every prior open P0. Do not turn unrelated newly noticed P1/P2 items into new blockers. A genuinely new P0 may still require revision.

## Claims

Create `CLAIM_LEDGER.json` from the reviewed evidence. Each paper-bearing claim records its exact text, scope, evidence IDs, evidence state, and limitations. Strong claims—global optimality, equivalence, causality, robustness, significance, or reproducibility—still need claim-specific support. `reproduced` requires an isolated rerun and comparison; an original successful run is only `supported_not_reproduced` unless stronger evidence exists.

Before paper writing, build `validation-paper`. Its compact payload contains the problem summary, model summary, verified results, selected claims, limitations, a draft figure/table representation plan, and identified official-format files. A fresh paper task reads this handoff first and does not scan full run/debug history.
