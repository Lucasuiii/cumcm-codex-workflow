# Stage 4: Computation

## Required outputs

- `code/` with runnable source
- `runs/<run-id>/RUN_MANIFEST.json`
- `runs/<run-id>/stdout.log` and `stderr.log`
- `runs/<run-id>/outputs/`
- `results/RESULTS_INDEX.json`

Run the actual code. Record the command, working directory, start and finish times, exit status, environment, dependencies, and seeds. Mark result-affecting inputs as `formal_input` and paper- or claim-bearing machine-readable outputs as `claim_bearing_output`; both require hashes. Mark non-result-affecting inputs as `auxiliary_input`, transient outputs as `intermediate_output`, and troubleshooting artifacts as `diagnostic_output`; these may omit hashes. Prefer the Git commit or source revision for code identity instead of hashing every source file.

Keep raw executed outputs immutable. Create derived tables or summaries separately and record their source run. Do not silently overwrite a previous run.

Every indexed result must point to an exact executed JSON value using `path#JSON-pointer`. Keep the unrounded value authoritative; record display rounding separately. A process exit code proves execution only, so preserve assertions, residuals, feasibility checks, or independent calculations appropriate to the model.

When simulation is required, record the generator, parameter source, seed, number of replications, Monte Carlo uncertainty, and the fact that the data are simulated. Never tune simulated data to ensure a preferred method wins.

Approximate optimization must report termination reason, incumbent objective, bound or gap when available, and repeated-seed stability when relevant.

Hash checks are automatic. Missing or empty run files and hash drift in formal inputs or claim-bearing outputs remain errors. An indexed result may point only to a declared `claim_bearing_output`. A stale byte-size field is a warning. Stdout, stderr, caches, temporary files, and derived presentation files do not need separate hashes unless they become formal evidence or delivery artifacts. Every v0.4 run input and output must declare its `evidence_role`; a missing role is a schema error.
