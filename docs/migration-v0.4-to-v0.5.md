# Migrate a v0.4 workspace

Use a new target directory:

```bash
python3 .agents/skills/cumcm-workflow/scripts/migrate_v04_to_v05.py \
  --source /path/to/v04-workspace \
  --target /path/to/v05-workspace
```

The source is never edited. The migrator:

- copies usable artifacts and removes cache/temp files from the copy;
- upgrades v0.5 contract envelopes and working-mode state;
- converts old review verdict/severity vocabulary when present;
- derives compatible claim/representation/paper-structure fields;
- binds existing editable LaTeX source when possible;
- marks all migrated runs `official_run: false`.

The last rule is intentional. v0.4 did not require the v0.5 selected-backend source snapshot, so migration cannot honestly claim the old run is bound to current executed code. Select MATLAB or Python, rerun claim-bearing computation, rebuild handoffs/review, and only then enter finalizing.
