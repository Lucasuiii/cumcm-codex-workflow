#!/usr/bin/env python3
"""Resolve the one canonical RESULTS_INDEX -> official run -> source chain."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from provenance import snapshot_matches


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def resolve_official_computation(project: Path, results: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Return referenced successful official runs or fail on any broken formal link."""
    project = project.resolve()
    results = results or read_object(project / "results" / "RESULTS_INDEX.json")
    result_items = results.get("results")
    if not isinstance(result_items, list) or not result_items:
        raise ValueError("RESULTS_INDEX.json must contain at least one formal result")

    referenced: set[str] = set()
    for item in result_items:
        if not isinstance(item, dict) or not str(item.get("run_id", "")).strip():
            raise ValueError("every formal result must reference a run_id")
        referenced.add(str(item["run_id"]))

    manifests: dict[str, tuple[str, dict[str, Any]]] = {}
    for manifest_path in sorted((project / "runs").glob("*/RUN_MANIFEST.json")):
        rel = manifest_path.relative_to(project).as_posix()
        run = read_object(manifest_path)
        run_id = str(run.get("run_id", "")).strip()
        if not run_id:
            continue
        if run_id in manifests:
            raise ValueError(f"duplicate run_id in RUN_MANIFEST files: {run_id}")
        manifests[run_id] = (rel, run)

    resolved: list[dict[str, Any]] = []
    for run_id in sorted(referenced):
        candidate = manifests.get(run_id)
        if candidate is None:
            raise ValueError(f"formal result references a missing run: {run_id}")
        manifest_path, run = candidate
        if run.get("official_run") is not True or run.get("status") != "completed" or run.get("exit_code") != 0:
            raise ValueError(f"formal result references a run that is not a successful official run: {run_id}")
        implementation = run.get("implementation") if isinstance(run.get("implementation"), dict) else {}
        snapshot = implementation.get("source_snapshot")
        if not snapshot_matches(project, snapshot):
            raise ValueError(f"formal result references an official run with a missing or stale source snapshot: {run_id}")

        output_roles = {
            str(entry.get("path")): entry.get("evidence_role")
            for entry in run.get("outputs", [])
            if isinstance(entry, dict) and entry.get("path")
        }
        for result in result_items:
            if not isinstance(result, dict) or str(result.get("run_id")) != run_id:
                continue
            locator = str(result.get("output_locator", ""))
            output_path = locator.split("#", 1)[0] if "#" in locator else ""
            if not output_path or output_roles.get(output_path) != "claim_bearing_output":
                raise ValueError(
                    f"formal result does not locate a claim-bearing output of official run {run_id}: "
                    f"{result.get('result_id')}"
                )

        resolved.append(
            {
                "run_id": run_id,
                "manifest_path": manifest_path,
                "manifest": run,
                "source_snapshot": snapshot,
                "source_files": [str(path) for path in snapshot.get("files", [])],
                "formal_inputs": [
                    str(entry.get("path"))
                    for entry in run.get("inputs", [])
                    if isinstance(entry, dict) and entry.get("evidence_role") == "formal_input"
                ],
                "claim_bearing_outputs": [
                    str(entry.get("path"))
                    for entry in run.get("outputs", [])
                    if isinstance(entry, dict) and entry.get("evidence_role") == "claim_bearing_output"
                ],
            }
        )
    return resolved
