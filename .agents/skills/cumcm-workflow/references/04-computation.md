# Stage 4: Computation

## Required outputs

- `code/` with runnable source
- `runs/<run-id>/RUN_MANIFEST.json`
- `runs/<run-id>/stdout.log` and `stderr.log`
- `runs/<run-id>/outputs/`
- `results/RESULTS_INDEX.json`

Run the actual code. Record the command, working directory, start and finish times, exit status, environment, dependencies, seeds, hashes for formal inputs, and hashes for claim-bearing machine-readable outputs. Prefer the Git commit or source revision for code identity instead of hashing every source file.

Keep raw executed outputs immutable. Create derived tables or summaries separately and record their source run. Do not silently overwrite a previous run.

Every indexed result must point to an exact executed JSON value using `path#JSON-pointer`. Keep the unrounded value authoritative; record display rounding separately. A process exit code proves execution only, so preserve assertions, residuals, feasibility checks, or independent calculations appropriate to the model.

When simulation is required, record the generator, parameter source, seed, number of replications, Monte Carlo uncertainty, and the fact that the data are simulated. Never tune simulated data to ensure a preferred method wins.

Approximate optimization must report termination reason, incumbent objective, bound or gap when available, and repeated-seed stability when relevant.

Hash checks are automatic. Missing or empty run files and hash drift in formal inputs or claim-bearing outputs remain errors. A stale byte-size field is a warning. Stdout, stderr, caches, temporary files, and derived presentation files do not need separate hashes unless they become formal evidence or delivery artifacts.
