# Computation responsibility

## Outcome

Produce one reliable official implementation, successful run evidence, and an exact result index. Working mode may keep exploratory and failed runs, but only a successful `official_run: true` run may support a formal result.

## Choose one backend

Use the project preference (`matlab` preferred, `python` fallback, `auto` selection) as a tie-break, not a mandate. Compare the actual task:

- MATLAB often fits numerical linear algebra, optimization, ODE/PDE, signal processing, and licensed toolbox workflows.
- Python often fits heterogeneous data cleaning, CSV/Excel automation, machine learning, text/web data, or an existing Python codebase.
- Availability, required toolbox/package, implementation complexity, existing code, and runtime stability override preference.

Run `scripts/backend_selection.py` when a recorded deterministic selection is useful. MATLAB detection checks explicit `implementation.matlab_executable`, then `matlab` on PATH, then macOS `/Applications/MATLAB_R*.app/bin/matlab` with newer releases first. A preferred or explicitly selected backend may fall back when unavailable; a task `required_backend` is a hard runtime requirement and must error rather than switch. Once selected, implement and officially execute that language only. Do not build a second backend for parity unless the user explicitly requests cross-implementation validation.

The mathematical formulation, variable meanings, result IDs, and acceptance checks remain language-neutral.

## Official run evidence

Each `RUN_MANIFEST.json` records:

- selected language, rationale, entry point, runtime, dependencies, and MATLAB toolboxes when applicable;
- a `sha256-tree-v1` source snapshot covering the executed code;
- argument array, working directory, timestamps, exit status, stdout/stderr, environment, seeds, and assertions;
- `formal_input` and `claim_bearing_output` hashes;
- `official_run: true` only for the run selected to support formal results.

Failed or exploratory runs may remain for local debugging with `official_run: false`; they do not block merely because they failed, and they do not enter handoffs or support claims.

Every result uses an exact `path#JSON-pointer` into a declared claim-bearing JSON output. Keep unrounded values authoritative and display rounding separate. A successful exit code proves execution, not model correctness, so include problem-specific feasibility, residual, conservation, baseline, or stability checks when they matter.

Before validation, build `modeling-computation` and `computation-validation` handoffs. The latter points to canonical official runs/results. Computation→validation, the independent package, and paper→delivery all resolve the same chain: `RESULTS_INDEX.json` → referenced successful `official_run: true` manifest → current source snapshot. A missing, failed, non-official, or stale link fails every consumer rather than being silently skipped. The context-separated reviewer package copies only the official inputs, problem/model contracts, results index, that resolved evidence, formal inputs, claim-bearing outputs, and review instructions. It excludes failed/exploratory runs and stdout/stderr/debug history.
