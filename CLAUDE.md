# CLAUDE.md

Engineering notes for working **on** this repository. To *use* the workflow on a contest problem, invoke the `cumcm-workflow` skill (`.claude/skills/cumcm-workflow/SKILL.md`) and follow `.agents/skills/cumcm-workflow/SKILL.md`.

## Layout

`.agents/skills/cumcm-workflow/` is the single canonical tree: `SKILL.md`, `references/`, `schemas/`, `scripts/`, `assets/`. `.claude/skills/cumcm-workflow/SKILL.md` is a thin router into it and deliberately restates no rules — if you add a rule, it goes in the canonical tree only.

## Invariants to preserve when editing

- **Machine facts are recorded, never hand-written.** If a change would make an agent type a SHA-256, an exit code, a page count or a result value into a contract, the change is wrong; extend a recorder instead.
- **Two knobs only.** `mode` (`working` / `finalizing`) and `--gate-mode` (`preflight` / `enforce`). Do not reintroduce a profile axis.
- **Four stage statuses.** `not_started`, `in_progress`, `passed`, `needs_revision`.
- **Schemas describe shape, the checker decides strictness.** Mode-dependent requirements (for example the frozen model contract) live in `workflow_checks.py`, not in a JSON Schema `required` list — a schema cannot see the mode.
- **A schema is also a prompt.** An optional field that nothing consumes will still get filled in by an agent. Delete it rather than leaving it optional.
- **Exploratory runs never block.** Anything about an `official_run: false` run is at most a warning.
- Do not add a check whose only evidence is that someone asserted it. If it cannot be measured, it belongs in `REVIEW_REQUEST.md` as a named failure class for a human or a fresh-context reviewer.
- **A free-text field is not a check.** `alternatives_considered` was a string array whose only rule was "non-empty", so "I compared alternatives" was unfalsifiable. Structured `candidates` replaced it because a candidate can be tied to the runs that evaluated it. Apply the same test to anything new: what would make this claim wrong, and can a script see it?
- **No backward compatibility.** v0.6 rejects any contract whose `schema_version` is not `0.6.0`, and the repository keeps no migration scripts or historical design documents. An older workspace is re-initialised from its official files.

## Development

```bash
python3 -m pip install -r requirements-ci.txt
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q .agents/skills/cumcm-workflow/scripts tests
```

`tests/test_v06_recorders.py` runs real subprocesses and a real `xelatex` compile; it skips the CJK case when the `ctex` class is not installed. Every other test file works on synthetic fixtures.

When you add a rule ID, add the test that makes it fire and the test that proves it does not fire in `working` mode.

## Version bumps

`WORKFLOW_VERSION` in `workflow_checks.py` and the recorders, the `const` in every schema, and `pyproject.toml`. The checker rejects any contract whose `schema_version` differs; that is intentional, and existing workspaces are re-initialised rather than migrated. Say so in the README when you bump.
