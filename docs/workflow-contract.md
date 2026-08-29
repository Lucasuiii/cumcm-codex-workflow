# Workflow contract

| Stage | Required review | May advance when |
|---|---|---|
| Intake | structural + human | official inputs are inventoried, hashed, and confirmed complete |
| Problem analysis | structural + human | facts, interpretation, assumptions, and capability coverage are approved |
| Model design | structural + human | model ownership, dependencies, alternatives, and optimality scope are approved |
| Computation | execution + numerical + human | code ran, immutable outputs are preserved, and indexed values match exact output locators |
| Validation | numerical + semantic + human | cross-question consistency, evidence states, strong-claim certificates, and limitations are approved |
| Paper | structural + visual + human | figures are traceable and the reviewer confirms no unindexed results were introduced during writing |
| Delivery | structural + execution + visual + human | compiled bytes, logs, warnings, hashes, and final review match the delivery manifest |

`strict` and `sprint` may differ in exploration and polish. Both block on source, execution, hash, contradiction, result-trace, cross-question, and claim-evidence errors. The final paper audit hook remains explicit and inactive unless requested.
