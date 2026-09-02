# Cross-stage handoffs

Handoffs are the durable interface for fresh-context work. Build them with:

```bash
python3 scripts/build_handoff.py --project <project> --transition <name>
```

Transitions are `modeling-computation`, `computation-validation`, `validation-paper`, and `paper-delivery`.

Each handoff contains canonical artifact paths and hashes, one upstream digest, a compact downstream payload, and an explicit list of excluded history. It points into the same workspace; it does not duplicate logs or outputs. The independent review package remains the context-separated payload for computation validation and adds copied materials because a reviewer may work outside the originating workspace.

The modeling handoff binds the official source manifest and official inputs needed by computation. The computation handoff binds only successful official runs referenced by formal results, their selected source snapshot, formal inputs, and claim-bearing outputs; failed/exploratory runs and full logs stay out. The paper handoff binds the official format files it names, so a changed rule or template makes the handoff stale.

The validation-paper payload contains problem/model summaries, verified results, selected claims, limitations, a draft figure/table plan, and identified official-format files. A fresh paper task reads this payload before opening upstream files.

If any canonical artifact changes, the handoff is stale. Rebuild it after the affected stage is revalidated. Do not patch digest fields manually.
