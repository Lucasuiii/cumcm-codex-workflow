# Limitations

- A completed workflow does not certify a correct model.
- Human reviewers and language models may share interpretation errors.
- Deterministic validators cannot establish global optimality, causal identification, or statistical validity without problem-specific evidence.
- Strong-claim certificate declarations are only traceable records; the validator does not prove that a mathematical certificate is valid.
- Code-entry and run links establish declared implementation and execution, but problem-specific tests are still needed to show the code matches the equations.
- Same-model logic review remains correlated even when run in a fresh context; v0.4 records that limitation and only prevents same-conversation review from satisfying the independent gate.
- Reproducibility requires preserved inputs and executable dependencies; proprietary solvers or unavailable data may limit reruns.
- Delivery compliance is limited to official materials supplied or explicitly identified by the user. Missing rules or templates block delivery until the user supplies them; autonomous search is not a substitute.
- The visible-text checker detects known workflow tokens, local paths, excessive decimal precision, and number-dense sentences. It cannot judge whether every sentence is elegant or every displayed precision is scientifically justified.
- Arbitrary prose-to-number tracing is not inferred from keyword matching; teams must use the result and claim ledgers deliberately.
- Final claim-level `model-xray` paper auditing is deferred and user-invoked.
