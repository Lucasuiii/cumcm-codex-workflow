# Stage 2: Problem analysis

## Required outputs

- `analysis/PROBLEM_FACTS.json`
- `analysis/TASK_CAPABILITIES.json`
- `analysis/ASSUMPTIONS.md`
- `analysis/SYMBOLS.md`

For each fact, cite an official source file and page, sheet, table, or cell range. Separate stated facts, interpretations, and added assumptions.

Translate each subproblem into observable capabilities: requested output, official facts used, acceptance checks, intended model owners, expected code entry points, and result IDs. Capability coverage is complete only when every requested subproblem output has an owner and a check that could fail.

Use stable fact and capability IDs. Do not treat a method name or keyword as implementation evidence. Identify ambiguous wording and compare plausible interpretations before choosing one.

Stop with `awaiting_review` and ask the user to approve the interpretation. Do not select a final model yet.
