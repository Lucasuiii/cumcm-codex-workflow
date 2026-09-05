# CUMCM 2024 B regression target

This fixture contains no official problem text, data, paper, or proprietary material. It records one behavioral invariant: optimizing over a fixed homogeneous policy class must not be presented as a global optimum over all feedback policies.

The executable synthetic project is constructed in `tests/test_workflow_core.py`. The tests verify that the scoped claim passes while a global-optimality overclaim without a certificate triggers `CLAIM-E011`. v0.6 regressions additionally cover working/finalizing modes, deferred model selection, P0-only review blocking, targeted re-review, source snapshots, handoff freshness, redo planning, and MATLAB/Python selection. `tests/test_recorders.py` covers the recorder chain end to end with real execution.
