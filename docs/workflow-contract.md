# Workflow contract

| Stage | Required review | May advance when |
|---|---|---|
| Intake | structural + human | official inputs are inventoried, hashed, and confirmed complete |
| Problem analysis | structural + human | facts, interpretation, assumptions, and capability coverage are approved |
| Model design | structural + human | model ownership, dependencies, alternatives, and optimality scope are approved |
| Computation | execution + numerical + human | code ran, immutable outputs are preserved, and indexed values match exact output locators |
| Validation | numerical + semantic + human | cross-question consistency, evidence states, strong-claim certificates, and limitations are approved |
| Paper | structural + semantic + visual + human | every question has a planned and reviewed argument chain; claims and figures have evidence jobs; critical issues are closed; content and all final pages are reviewed against exact bytes |
| Delivery | structural + execution + visual + human | compile receipt, reviewed PDF, page count, logs, diagnostics, delivery manifest, and version-bound decision agree |

`strict` and `sprint` may differ in exploration and polish. Both block on official-source hashes, formal run input and claim-bearing output hashes, frozen delivery hashes, execution, contradiction, result-trace, cross-question, claim-evidence, open-P0, final-version, and decision-scope errors. Editing-stage figure drift and redundant byte-size mismatches are warnings. A final PDF requires complete rendered-page coverage in either profile.

`preflight` distinguishes “automation complete, waiting for a person” from a failed build. It does not demote stale decisions, hash drift, missing evidence, failed content/layout checks, or compile mismatch. `enforce` is required before a stage is treated as passed.
