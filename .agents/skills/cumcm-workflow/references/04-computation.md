# Stage 4: Computation

## Required outputs

- `code/` with runnable source
- `runs/<run-id>/RUN_MANIFEST.json`
- `runs/<run-id>/logs/`
- `runs/<run-id>/outputs/`
- `results/RESULTS.md`

Run the actual code. Record the command, working directory, start and finish times, exit status, environment, dependencies, seeds, input hashes, and output hashes.

Keep raw executed outputs immutable. Create derived tables or summaries separately and record their source run. Do not silently overwrite a previous run.

When simulation is required, record the generator, parameter source, seed, number of replications, Monte Carlo uncertainty, and the fact that the data are simulated. Never tune simulated data to ensure a preferred method wins.

Approximate optimization must report termination reason, incumbent objective, bound or gap when available, and repeated-seed stability when relevant.
