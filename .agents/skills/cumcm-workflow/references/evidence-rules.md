# Evidence rules

## Three levels

- Hard invariant / P0: affects truth, provenance, reproducibility, task coverage, or final submission identity. Block it.
- Warning / P1: affects model strength or reader confidence but does not show the result is false. Keep it visible.
- Suggestion / P2: optional expression, layout, or extra analysis. Do not gate on it.

File existence proves existence. Schema validity proves structure. Successful execution proves a process ran. None proves that the model matches the task. Exact locators and hashes establish identity, not mathematical correctness.

Claims of global optimality, equivalence, causality, significance, robustness, or reproducibility require claim-specific evidence and scope. A solver success flag, non-rejection, or original run is insufficient by itself.

## Change impact

- `cosmetic`: reader-facing style/layout only; recheck paper and delivery bindings.
- `local`: recheck the owning component.
- `semantic`: recheck the owner and affected downstream stages.
- `claim_changing`: recheck computation, validation, paper, and delivery.
- `global`: full staged revalidation.

Do not infer `global` merely because several files changed. Use stage snapshots and canonical handoff digests to find the actual impact. Hard invariants remain checkable even when an unchanged stage snapshot is trusted.
