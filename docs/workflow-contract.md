# Workflow contract

| Responsibility | Hard invariant | Non-blocking concern |
|---|---|---|
| Intake | official inputs preserved and correctly identified | optional source metadata polish |
| Modeling | every official subproblem has an owned output; model scope does not contradict the task | alternative model breadth, stronger assumptions |
| Computation | one successful official backend, current source snapshot, formal inputs/outputs, exact result locator | extra assertions or diagnostics |
| Validation | fresh package, no open P0, claims have evidence and scope | P1 validation/sensitivity/generalization concern; P2 suggestion |
| Paper | every subproblem answered; no invented results or visible internal metadata; no open paper P0 | chart density, section strength, optional polish |
| Delivery | exact reviewed PDF, current editable source snapshot, successful compile, official-format review, three delivery roles | non-critical presentation improvements |

Working mode can proceed with incomplete downstream artifacts. Finalizing enforce requires all stages through the target to be passed and covered by current accepted decisions. A state edit cannot substitute for a decision.

Independent review begins with a full pass. If it returns P0 findings, the next pass defaults to targeted re-review. `accepted_with_concerns` is sufficient to enter paper work because open P1 items do not demonstrate false results.

Change impact controls revalidation scope. Cosmetic and local changes do not trigger full-workspace review. Semantic, claim-changing, and global changes expand only as far as their downstream consequences require.
