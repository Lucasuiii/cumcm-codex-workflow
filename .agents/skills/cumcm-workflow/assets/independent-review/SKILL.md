---
name: cumcm-independent-review
description: Independently review a CUMCM computation package before its claims enter validation or paper writing. Use only inside a generated independent-review package.
---

# CUMCM Independent Review

Review this package without consulting the originating conversation. Treat every supplied conclusion as untrusted and reconstruct the task from the official inputs, contracts, code, run records, and executed outputs.

## Boundaries

- Work read-only inside the package.
- Do not search for missing official materials. Report them as missing.
- Do not edit, rerun, or replace the preserved execution unless the user separately authorizes a reproduction run.
- File existence and successful execution do not prove that the model answers the official question.
- Give exact file, formula, code, or numerical locations for every finding.
- Preserve negative and inconclusive findings verbatim.

## Review order

1. Read `REVIEW_REQUEST.md` and `materials/problem/SOURCE_MANIFEST.json`.
2. Reconstruct each subproblem from the supplied official files and `PROBLEM_FACTS.json`.
3. Compare the official request with the model objective, variables, constraints, assumptions, and cross-question dependencies.
4. Inspect computation entry points, run manifests, executed outputs, and result locators.
5. Challenge at least these failure classes:
   - task or target misunderstood;
   - upper/lower bound or optimization direction reversed;
   - a quantity counted twice;
   - unsupported extrapolation;
   - an observed variable omitted without justification;
   - cross-question contradiction;
   - code and mathematical formulation disagree;
   - numerical output violates units, bounds, conservation, or official constraints.
6. Write the raw review to `INDEPENDENT_REVIEW_RAW.md` and the structured result to `INDEPENDENT_REVIEW_RESULT.json` using the supplied schema example.

## Verdict

- `accepted`: no fatal or unresolved major defect was found in the reviewed scope.
- `revision_requested`: at least one fatal or unresolved major defect requires returning to model design or computation.
- `inconclusive`: required material is missing or the available evidence cannot support a decision.

State the reviewer, model if applicable, task reference, whether this is a different conversation, and the appropriate independence grade. Never describe a same-context review as independent.
