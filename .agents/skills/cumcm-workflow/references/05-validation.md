# Validation responsibility

## First review: full and context-separated

Build the current computation handoff, then run:

```bash
python3 scripts/build_independent_review_package.py --project <project>
```

The package binds only canonical evidence for formal results: official inputs, problem/model contracts, `RESULTS_INDEX.json`, cited successful `official_run: true` manifests, matching source snapshots, formal inputs, claim-bearing outputs, and review instructions. Failed/exploratory runs, stdout/stderr, full logs, and debug history are excluded; package/upstream freshness digests cover this same canonical set. Stop and let the user route it to a separate task or human. Record both originating and reviewer task references; they must differ. Same-model fresh-context review remains correlated. Task references and user confirmation improve context-separation evidence but cannot cryptographically prove reviewer independence.

## Findings and verdicts

- `P0`: actual data/computation error, task mismatch, unsupported key claim, code/model/result disagreement, or serious provenance failure.
- `P1`: concern about model choice, assumptions, baseline, validation, sensitivity, or generalization.
- `P2`: optional presentation or additional experiment suggestion.

Verdicts are `accepted`, `accepted_with_concerns`, `revision_required`, and `inconclusive`. Only an open P0 permits `revision_required`. Open P1/P2 items remain visible as warnings or suggestions and do not block paper work.

After a full review returns open P0 findings, rerunning the package builder in auto mode defaults to a targeted re-review. It archives the prior review/package and targets every prior open P0. The new package embeds `TARGETED_FINDINGS.json` with only `finding_id`, `category`, `location`, `evidence`, and `recommendation`, so a fresh reviewer can work from the package alone without receiving the full old review. Do not turn unrelated newly noticed P1/P2 items into new blockers. A genuinely new P0 may still require revision.

## Claims

Create `CLAIM_LEDGER.json` from the reviewed evidence. Each paper-bearing claim records its exact text, scope, evidence IDs, evidence state, and limitations. Strong claims—global optimality, equivalence, causality, robustness, significance, or reproducibility—still need claim-specific support. `reproduced` requires an isolated rerun and comparison; an original successful run is only `supported_not_reproduced` unless stronger evidence exists.

Before paper writing, build `validation-paper`. Its limitations come from claim limitations, unresolved/accepted P1 concerns, and explicit model applicability, assumptions, and known limitations—not model `scope`. Its `representation_candidates` proactively identify trend, multi-group comparison, distribution, sensitivity, model-performance, and spatial/network/clustering evidence. A fresh paper task reads this compact handoff first, chooses prose/equation/table/figure, and does not scan full run/debug history.
