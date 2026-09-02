# Cross-stage handoffs

Handoffs are the durable interface for fresh-context work. Build them with:

```bash
python3 scripts/build_handoff.py --project <project> --transition <name>
```

Transitions are `modeling-computation`, `computation-validation`, `validation-paper`, and `paper-delivery`.

Each handoff contains canonical artifact paths and hashes, one upstream digest, a compact downstream payload, and an explicit list of excluded history. It points into the same workspace; it does not duplicate logs or outputs. The independent review package remains the context-separated payload for computation validation and copies only canonical evidence for formally indexed results because a reviewer may work outside the originating workspace. Its digest excludes failed/exploratory runs, stdout/stderr, and debug history.

The modeling handoff binds the official source manifest and official inputs needed by computation. The computation handoff binds only successful official runs referenced by formal results, their selected source snapshot, formal inputs, and claim-bearing outputs; failed/exploratory runs and full logs stay out. The paper handoff binds the official format files it names, so a changed rule or template makes the handoff stale.

The validation-paper payload contains problem/model summaries, verified results, selected claims, real claim/P1/model limitations, proactive `representation_candidates`, and identified official-format files. Model `scope` is not treated as a limitation. Candidates flag trends, comparisons, distributions, sensitivity, model performance, and spatial/network/clustering structures without requiring an existing figure or prescribing a minimum count. A fresh paper task reads this payload before opening upstream files and chooses prose, equation, table, or figure.

If any canonical artifact changes, the handoff is stale. Rebuild it after the affected stage is revalidated. Do not patch digest fields manually.
