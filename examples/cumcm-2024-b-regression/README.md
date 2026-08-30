# CUMCM 2024 B regression target

This fixture contains no official problem text, data, paper, or proprietary material. It records one behavioral invariant: optimizing over a fixed homogeneous policy class must not be presented as a global optimum over all feedback policies.

The executable synthetic project is constructed in `tests/test_workflow_core.py`. The tests verify that the scoped claim passes while a global-optimality overclaim without a certificate triggers `CLAIM-E011`. They also exercise source-hash drift, result/output disagreement, cross-question unit conflicts, explicit evidence roles, and artifact-bound decisions.
