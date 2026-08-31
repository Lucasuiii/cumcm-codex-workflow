# Workflow contract

| Stage | Required review | May advance when |
|---|---|---|
| Intake | structural + human | user-supplied official inputs are inventoried, byte-identified, and confirmed complete |
| Problem analysis | structural + human | facts, interpretation, assumptions, and capability coverage are approved |
| Model design | structural + human | model ownership, dependencies, alternatives, and optimality scope are approved |
| Computation | execution + numerical + human | code ran, immutable outputs are preserved, and indexed values match exact output locators |
| Validation | independent + numerical + semantic + human | a user-selected separate reviewer has checked the packaged evidence; cross-question consistency, evidence states, strong-claim certificates, and limitations are approved |
| Paper | structural + semantic + visual + human | every question has a planned and reviewed problem-solving narrative; internal metadata remains sidecar-only; numerical presentation flags and critical issues are closed; content and all final pages are reviewed against the exact PDF |
| Delivery | structural + execution + visual + human | user-supplied compliance materials, compile receipt, reviewed PDF, editable LaTeX, computation source, diagnostics, delivery manifest, and version-bound decision agree |

`strict` and `sprint` may differ in exploration and polish. Both block on official-source identity, formal run input and claim-bearing output identity, the exact final-PDF identity, execution, contradiction, result trace, cross-question consistency, independent-review defects, claim evidence, open P0 issues, final-version mismatches, and stale approval scope. Editing-stage figure digest drift and redundant byte-size mismatches are warnings. A final PDF requires complete rendered-page coverage in either profile.

`preflight` distinguishes “automation complete, waiting for a person” from a failed build. It does not demote stale decisions, required-identity drift, missing evidence, failed independent/content/layout checks, or compile mismatch. `enforce` is required before a stage is treated as passed.
