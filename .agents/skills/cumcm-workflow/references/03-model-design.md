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

Plan meaningful checks appropriate to the actual claims: hand-solvable instance, extreme case, conservation law, out-of-sample test, residual analysis, or perturbation analysis. An independent second implementation is optional and must not be created merely for MATLAB/Python parity.

Before computation finalization, obtain approval of the selected model and scope, then build the `modeling-computation` handoff. A computation task reads that handoff rather than the full modeling conversation.
