#!/usr/bin/env python3
"""Build compact, freshness-bound cross-stage handoffs for fresh-context tasks."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from provenance import digest_records, sha256_file


WORKFLOW_VERSION = "0.5.0"
TRANSITIONS = {
    "modeling-computation": ("model-design", "computation"),
    "computation-validation": ("computation", "validation"),
    "validation-paper": ("validation", "paper"),
    "paper-delivery": ("paper", "delivery"),
}
BASE_PATHS = {
    "modeling-computation": [
        ("problem/SOURCE_MANIFEST.json", "source_manifest"),
        ("analysis/PROBLEM_FACTS.json", "problem"),
        ("analysis/TASK_CAPABILITIES.json", "capabilities"),
        ("model/MODEL_CONTRACT.json", "model"),
        ("model/CROSS_QUESTION_LEDGER.json", "cross_question"),
    ],
    "computation-validation": [
        ("model/MODEL_CONTRACT.json", "model"),
        ("results/RESULTS_INDEX.json", "results"),
    ],
    "validation-paper": [
        ("problem/SOURCE_MANIFEST.json", "source_manifest"),
        ("analysis/PROBLEM_FACTS.json", "problem"),
        ("model/MODEL_CONTRACT.json", "model"),
        ("results/RESULTS_INDEX.json", "results"),
        ("validation/INDEPENDENT_REVIEW_RESULT.json", "review"),
        ("validation/CLAIM_LEDGER.json", "claims"),
    ],
    "paper-delivery": [
        ("paper/PAPER_PLAN.json", "paper_plan"),
        ("paper/LATEX_TEMPLATE_MANIFEST.json", "latex_source"),
        ("paper/PAPER_QUALITY_REPORT.json", "paper_quality"),
        ("paper/PAPER_VISIBLE_TEXT_REPORT.json", "visible_text"),
    ],
}


def official_sources(root: Path) -> list[dict[str, Any]]:
    sources = read_object(root, "problem/SOURCE_MANIFEST.json")
    return [
        item for item in sources.get("sources", [])
        if isinstance(item, dict) and item.get("origin") in {"official", "organizer_attachment"}
    ]


def is_format_source(source: dict[str, Any]) -> bool:
    tags = " ".join(str(value) for value in source.get("authoritative_for", [])).casefold()
    name = str(source.get("path", "")).casefold()
    return any(token in tags or token in name for token in ("format", "rule", "template", "格式", "规则", "模板"))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def read_object(root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {rel}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {rel}")
    return value


def add_artifact(root: Path, records: list[dict[str, str]], rel: str, role: str) -> None:
    path = (root / rel).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"handoff path escapes project: {rel}") from exc
    if not path.is_file():
        raise ValueError(f"handoff artifact is missing: {rel}")
    if rel not in {item["path"] for item in records}:
        records.append({"path": rel, "role": role, "sha256": sha256_file(path)})


def paper_payload(root: Path) -> dict[str, Any]:
    facts = read_object(root, "analysis/PROBLEM_FACTS.json")
    model = read_object(root, "model/MODEL_CONTRACT.json")
    results = read_object(root, "results/RESULTS_INDEX.json")
    claims = read_object(root, "validation/CLAIM_LEDGER.json")
    supported_states = {"supported_not_reproduced", "reproduced", "partially_supported"}
    verified_results = [
        {key: item.get(key) for key in ("result_id", "name", "value", "unit", "scope", "evidence_state")}
        for item in results.get("results", [])
        if isinstance(item, dict) and item.get("evidence_state") in supported_states
    ]
    selected_claims = [
        {key: item.get(key) for key in ("claim_id", "text", "scope", "evidence_state", "limitations")}
        for item in claims.get("claims", [])
        if isinstance(item, dict) and item.get("evidence_state") in supported_states
    ]
    representation_plan = []
    for item in claims.get("claims", []):
        if not isinstance(item, dict) or item.get("evidence_state") not in supported_states:
            continue
        evidence = item.get("evidence") if isinstance(item.get("evidence"), dict) else {}
        result_count = len(evidence.get("result_ids", []))
        medium = "figure" if evidence.get("figure_ids") else "table" if result_count > 1 else "prose"
        representation_plan.append(
            {"claim_id": item.get("claim_id"), "medium": medium, "reason": "draft choice from verified evidence shape"}
        )
    official_format_files = [source.get("path") for source in official_sources(root) if is_format_source(source)]
    return {
        "problem_summary": [
            {"subproblem_id": item.get("subproblem_id"), "request": item.get("request"), "expected_output": item.get("expected_output")}
            for item in facts.get("subproblems", []) if isinstance(item, dict)
        ],
        "model_summary": [
            {"model_id": item.get("model_id"), "method": item.get("method"), "scope": item.get("scope")}
            for item in model.get("components", []) if isinstance(item, dict)
        ],
        "verified_results": verified_results,
        "claims": selected_claims,
        "limitations": sorted({str(item.get("scope")) for item in model.get("components", []) if isinstance(item, dict) and item.get("scope")}),
        "figure_table_plan": representation_plan,
        "official_format_files": official_format_files,
    }


def build_payload(root: Path, transition: str, state: dict[str, Any]) -> dict[str, Any]:
    if transition == "modeling-computation":
        return {"implementation": state.get("implementation"), "next_task": "select one backend, implement, execute, and preserve the official run"}
    if transition == "computation-validation":
        results = read_object(root, "results/RESULTS_INDEX.json")
        referenced = {str(item.get("run_id")) for item in results.get("results", []) if isinstance(item, dict) and item.get("run_id")}
        official = []
        for manifest in sorted((root / "runs").glob("*/RUN_MANIFEST.json")):
            run = read_object(root, manifest.relative_to(root).as_posix())
            if run.get("run_id") in referenced and run.get("official_run") is True and run.get("status") == "completed" and run.get("exit_code") == 0:
                official.append(str(run["run_id"]))
        return {"official_run_ids": sorted(official), "next_task": "review the packaged computation without reading debug history"}
    if transition == "validation-paper":
        return paper_payload(root)
    quality = read_object(root, "paper/PAPER_QUALITY_REPORT.json")
    latex = read_object(root, "paper/LATEX_TEMPLATE_MANIFEST.json")
    return {"approved_pdf": quality.get("paper_artifact"), "latex_entrypoint": latex.get("main_path"), "required_source_files": latex.get("required_files", [])}


def build(root: Path, transition: str) -> Path:
    root = root.resolve()
    if transition not in TRANSITIONS:
        raise ValueError(f"unknown transition: {transition}")
    state = read_object(root, ".cumcm/state.json")
    if state.get("workflow_version") != WORKFLOW_VERSION:
        raise ValueError(f"handoff builder requires workflow {WORKFLOW_VERSION}")
    records: list[dict[str, str]] = []
    for rel, role in BASE_PATHS[transition]:
        add_artifact(root, records, rel, role)
    if transition == "modeling-computation":
        for source in official_sources(root):
            add_artifact(root, records, str(source.get("path")), "official_input")
    if transition == "computation-validation":
        results = read_object(root, "results/RESULTS_INDEX.json")
        referenced_run_ids = {
            str(item.get("run_id")) for item in results.get("results", [])
            if isinstance(item, dict) and item.get("run_id")
        }
        for manifest in sorted((root / "runs").glob("*/RUN_MANIFEST.json")):
            rel_manifest = manifest.relative_to(root).as_posix()
            run = read_object(root, rel_manifest)
            if run.get("run_id") not in referenced_run_ids or run.get("official_run") is not True or run.get("status") != "completed" or run.get("exit_code") != 0:
                continue
            add_artifact(root, records, rel_manifest, "official_run")
            implementation = run.get("implementation") if isinstance(run.get("implementation"), dict) else {}
            snapshot = implementation.get("source_snapshot") if isinstance(implementation.get("source_snapshot"), dict) else {}
            for rel in snapshot.get("files", []):
                add_artifact(root, records, str(rel), "computation_source")
            for item in run.get("inputs", []):
                if isinstance(item, dict) and item.get("evidence_role") == "formal_input":
                    add_artifact(root, records, str(item.get("path")), "formal_input")
            for item in run.get("outputs", []):
                if isinstance(item, dict) and item.get("evidence_role") == "claim_bearing_output":
                    add_artifact(root, records, str(item.get("path")), "claim_bearing_output")
    if transition == "validation-paper":
        for source in official_sources(root):
            if is_format_source(source):
                add_artifact(root, records, str(source.get("path")), "official_format")
    if transition == "paper-delivery":
        latex = read_object(root, "paper/LATEX_TEMPLATE_MANIFEST.json")
        for rel in latex.get("required_files", []):
            add_artifact(root, records, str(rel), "editable_source")
        quality = read_object(root, "paper/PAPER_QUALITY_REPORT.json")
        if isinstance(quality.get("paper_artifact"), dict):
            add_artifact(root, records, str(quality["paper_artifact"].get("path")), "approved_pdf")
    upstream, downstream = TRANSITIONS[transition]
    handoff = {
        "schema_version": WORKFLOW_VERSION,
        "artifact_type": "stage_handoff",
        "project_id": state.get("project_id"),
        "updated_at": utc_now(),
        "producer": {"kind": "script", "name": "build_handoff.py", "version": WORKFLOW_VERSION},
        "transition": transition,
        "upstream_stage": upstream,
        "downstream_stage": downstream,
        "upstream_digest": digest_records(records),
        "canonical_artifacts": sorted(records, key=lambda item: item["path"]),
        "payload": build_payload(root, transition, state),
        "excluded_history": ["full logs", "failed runs", "debug transcripts", "old review conversations"],
    }
    destination = root / "handoffs" / transition / "HANDOFF.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=destination.parent, delete=False) as stream:
        json.dump(handoff, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temp_name = stream.name
    os.replace(temp_name, destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a compact v0.5 cross-stage handoff")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--transition", required=True, choices=sorted(TRANSITIONS))
    args = parser.parse_args()
    try:
        destination = build(args.project, args.transition)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"wrote fresh handoff: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
