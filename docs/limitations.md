# Limitations

- Passing v0.5 does not certify a correct model, statistical design, or global optimum.
- Context separation reduces contamination but does not prove reviewer independence. Origin/reviewer task references remain user- and tool-recorded evidence.
- A same-model fresh task remains correlated.
- Backend selection uses declared task features and runtime availability; it cannot benchmark every MATLAB toolbox or Python package automatically.
- Source-tree and file digests establish identity, not that code implements the intended equations.
- Targeted re-review depends on correct P0 classification. A reviewer may miss a severe issue or overstate a concern.
- Stage impact classification is judgmental. Hard invariants are still checked to limit under-scoping risk.
- The visible-text checker catches known internal IDs and common local-home paths; it cannot recognize every sensitive string or judge prose quality.
- The generic LaTeX scaffold is submission-neutral. Current official compliance depends on user-supplied rules/templates.
- Migration preserves v0.4 artifacts but deliberately does not recertify old runs.
- Final claim-level `model-xray` auditing remains optional and user-invoked.
