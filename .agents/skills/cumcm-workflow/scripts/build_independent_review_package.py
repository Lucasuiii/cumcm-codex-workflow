#!/usr/bin/env python3
"""Build a read-only, conclusion-withheld package for pre-validation review."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from workflow_checks import WORKFLOW_VERSION, read_json, safe_project_path


PACKAGE_REL = Path("validation/independent-review-package")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def require_object(path: Path) -> dict[str, Any]:
    value, error = read_json(path)
    if error or not isinstance(value, dict):
        raise ValueError(f"cannot read JSON object {path}: {error or 'not an object'}")
    return value


def copy_material(project: Path, staging: Path, rel: str, role: str, records: list[dict[str, Any]], seen: set[str]) -> None:
    if rel in seen:
        return
    source = safe_project_path(project, rel)
    if source is None or not source.is_file() or source.stat().st_size == 0:
        raise ValueError(f"required review material is missing or unsafe: {rel}")
    destination = staging / "materials" / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    package_path = (PACKAGE_REL / "materials" / rel).as_posix()
    records.append({"path": package_path, "role": role, "size": destination.stat().st_size})
    seen.add(rel)


def build(project: Path) -> Path:
    project = project.resolve()
    destination = project / PACKAGE_REL
    if destination.exists():
        raise ValueError(f"refusing to overwrite existing review package: {destination}")

    state = require_object(project / ".cumcm/state.json")
    if state.get("workflow_version") != WORKFLOW_VERSION:
        raise ValueError(f"independent review packaging requires workflow {WORKFLOW_VERSION}")
    project_id = str(state.get("project_id", ""))
    if not project_id:
        raise ValueError("workflow state has no project_id")

    sources = require_object(project / "problem/SOURCE_MANIFEST.json")
    capabilities = require_object(project / "analysis/TASK_CAPABILITIES.json")
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    validation_dir = project / "validation"
    validation_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="independent-review-", dir=validation_dir) as temp:
        staging = Path(temp) / "package"
        staging.mkdir()
        asset_root = Path(__file__).resolve().parents[1] / "assets" / "independent-review"
        for name in ("SKILL.md", "REVIEW_REQUEST.md"):
            shutil.copy2(asset_root / name, staging / name)
            records.append(
                {
                    "path": (PACKAGE_REL / name).as_posix(),
                    "role": "review_instruction",
                    "size": (staging / name).stat().st_size,
                }
            )

        contract_roles = {
            "problem/SOURCE_MANIFEST.json": "problem_contract",
            "analysis/PROBLEM_FACTS.json": "problem_contract",
            "analysis/TASK_CAPABILITIES.json": "problem_contract",
            "model/MODEL_CONTRACT.json": "model_contract",
            "model/CROSS_QUESTION_LEDGER.json": "model_contract",
            "model/VALIDATION_PLAN.md": "model_contract",
            "results/RESULTS_INDEX.json": "run_record",
        }
        for rel, role in contract_roles.items():
            copy_material(project, staging, rel, role, records, seen)

        for source in sources.get("sources", []):
            if isinstance(source, dict) and source.get("origin") in {"official", "organizer_attachment"}:
                copy_material(project, staging, str(source.get("path")), "official_input", records, seen)

        for capability in capabilities.get("capabilities", []):
            if not isinstance(capability, dict):
                continue
            for entry in capability.get("code_entry_points", []):
                rel = str(entry).split(":", 1)[0]
                copy_material(project, staging, rel, "computation_source", records, seen)

        for manifest_path in sorted((project / "runs").glob("*/RUN_MANIFEST.json")):
            rel_manifest = manifest_path.relative_to(project).as_posix()
            copy_material(project, staging, rel_manifest, "run_record", records, seen)
            run = require_object(manifest_path)
            for field in ("stdout_path", "stderr_path"):
                if run.get(field):
                    log_path = safe_project_path(project, run[field])
                    if log_path is not None and log_path.is_file() and log_path.stat().st_size > 0:
                        copy_material(project, staging, str(run[field]), "run_record", records, seen)
            for entry in [*run.get("inputs", []), *run.get("outputs", [])]:
                if not isinstance(entry, dict) or not entry.get("path"):
                    continue
                role = "executed_output" if entry in run.get("outputs", []) else "run_record"
                copy_material(project, staging, str(entry["path"]), role, records, seen)

        result_template = {
            "schema_version": WORKFLOW_VERSION,
            "artifact_type": "independent_review_result",
            "project_id": project_id,
            "updated_at": None,
            "producer": {"kind": "external_tool", "name": "selected independent reviewer", "version": None},
            "review": {"decision": "unreviewed", "reviewer": None, "reviewed_at": None, "scope": "imported independent review", "notes": None},
            "package_manifest_path": (PACKAGE_REL / "REVIEW_PACKAGE_MANIFEST.json").as_posix(),
            "reviewer_context": {
                "reviewer_kind": "same_model_new_context",
                "reviewer": "REPLACE",
                "model": "REPLACE",
                "task_ref": "REPLACE",
                "different_conversation": True,
                "selected_by_user": True,
                "independence_grade": "context_separated_model_correlated",
            },
            "verdict": "inconclusive",
            "findings": [],
            "raw_review_path": "validation/INDEPENDENT_REVIEW_RAW.md",
            "reviewed_files": [],
        }
        (staging / "INDEPENDENT_REVIEW_RESULT_TEMPLATE.json").write_text(
            json.dumps(result_template, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        records.append(
            {
                "path": (PACKAGE_REL / "INDEPENDENT_REVIEW_RESULT_TEMPLATE.json").as_posix(),
                "role": "review_instruction",
                "size": (staging / "INDEPENDENT_REVIEW_RESULT_TEMPLATE.json").stat().st_size,
            }
        )

        generated_at = utc_now()
        manifest = {
            "schema_version": WORKFLOW_VERSION,
            "artifact_type": "independent_review_package",
            "project_id": project_id,
            "updated_at": generated_at,
            "producer": {"kind": "script", "name": "build_independent_review_package.py", "version": WORKFLOW_VERSION},
            "review": {"decision": "unreviewed", "reviewer": None, "reviewed_at": None, "scope": "package completeness and reviewer selection", "notes": None},
            "package_root": PACKAGE_REL.as_posix(),
            "review_skill_path": (PACKAGE_REL / "SKILL.md").as_posix(),
            "review_request_path": (PACKAGE_REL / "REVIEW_REQUEST.md").as_posix(),
            "conclusions_withheld": True,
            "files": sorted(records, key=lambda item: item["path"]),
            "reviewer_selection": {"status": "unreviewed", "selected_by": None, "reviewer": None, "model": None, "task_ref": None},
        }
        (staging / "REVIEW_PACKAGE_MANIFEST.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        shutil.copytree(staging, destination)
    return destination / "REVIEW_PACKAGE_MANIFEST.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the user-routed independent review package before validation")
    parser.add_argument("--project", required=True, type=Path)
    args = parser.parse_args()
    try:
        manifest = build(args.project)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"created independent review package: {manifest}")
    print("stop here: the user must choose a separate reviewer and return the structured result")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
