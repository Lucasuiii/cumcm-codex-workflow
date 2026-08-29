# Stage 3: Model design

## Required outputs

- `model/MODEL_CANDIDATES.md`
- `model/MODEL_CONTRACT.json`
- `model/CROSS_QUESTION_LEDGER.json`
- `model/OPTIMALITY_SCOPE.md`
- `model/VALIDATION_PLAN.md`

Compare candidates using fit to the task contract, identifiability, data requirements, computation cost, interpretability, and validation opportunities. Do not force multiple models when one is clearly sufficient.

For the selected model, define state, decisions, parameters, objective, constraints, observation mechanism, stochastic assumptions, and numerical method. Declare whether an optimum is exact, local, heuristic, relaxed, sampled, or restricted to a stated policy class.

Map every capability to a model component. Record each shared quantity's producer, consumers, definition, unit, time basis, transformation, uncertainty propagation, and authoritative artifact in the cross-question ledger. Resolve incompatible reuse before computation.

Plan at least one meaningful check appropriate to the problem: hand-solvable instance, extreme case, independent algorithm, conservation law, out-of-sample test, residual analysis, or perturbation analysis.

Stop for user approval of the selected model and its scope.
