#!/usr/bin/env python3
"""Audit a v0.1 project and optionally migrate only its workflow state.

Evidence-bearing contracts are never inferred. The tool reports the manual
work needed for v0.2 and preserves the original state before any write.
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from workflow_checks import STAGES, STAGE_STATUSES


def analyze(root: Path) -> dict:
    findings: list[dict] = []
    state_path = root / ".cumcm" / "state.json"
    state = None
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append({"severity": "error", "artifact": str(state_path), "message": str(exc)})

    if isinstance(state, dict):
        if state.get("workflow_version") == "0.2.0":
            findings.append({"severity": "info", "artifact": ".cumcm/state.json", "message": "state already declares v0.2.0"})
        else:
            current = state.get("current_stage")
            stages = state.get("stages")
            if current not in STAGES or not isinstance(stages, dict):
                findings.append({"severity": "error", "artifact": ".cumcm/state.json", "message": "v0.1 state shape is not recognized"})
            else:
                invalid = {key: value for key, value in stages.items() if key not in STAGES or value not in STAGE_STATUSES}
                if invalid:
                    findings.append({"severity": "error", "artifact": ".cumcm/state.json", "message": f"invalid stage entries: {invalid}"})

    mappings = [
        ("analysis/TASK_CONTRACT.json", "analysis/TASK_CAPABILITIES.json", "manual capability and acceptance-check mapping required"),
        ("model/MODEL_SPEC.md", "model/MODEL_CONTRACT.json", "manual variables, scope, ownership, and verification mapping required"),
        ("results/RESULTS.md", "results/RESULTS_INDEX.json", "rerun-backed exact JSON locators required"),
        ("validation/CLAIM_LEDGER.json", "validation/CLAIM_LEDGER.json", "map supported to supported_not_reproduced; do not infer reproduced"),
    ]
    for old, new, note in mappings:
        if (root / old).exists():
            findings.append({"severity": "warning", "artifact": old, "target": new, "message": note})

    return {
        "report_version": "0.2.0",
        "project_root": str(root.resolve()),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "findings": findings,
        "evidence_boundary": "The migration audit does not infer missing model, execution, result, or claim evidence.",
    }


def migrate_state(root: Path) -> None:
    state_path = root / ".cumcm" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("workflow_version") == "0.2.0":
        raise ValueError("state is already v0.2.0")
    if state.get("current_stage") not in STAGES or not isinstance(state.get("stages"), dict):
        raise ValueError("v0.1 state shape is not recognized")
    backup = root / ".cumcm" / "state.v0.1.json"
    if backup.exists():
        raise ValueError(f"backup already exists: {backup}")
    shutil.copy2(state_path, backup)
    migrated = {
        "schema_version": "0.2.0",
        "artifact_type": "workflow_state",
        "project_id": root.name,
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "producer": {"kind": "script", "name": "migrate_v01.py", "version": "0.2.0"},
        "review": {
            "decision": "unreviewed",
            "reviewer": None,
            "reviewed_at": None,
            "scope": "state migration only",
            "notes": "Evidence-bearing contracts require manual migration.",
        },
        "workflow_version": "0.2.0",
        "current_stage": state["current_stage"],
        "stages": {stage: state["stages"].get(stage, "not_started") for stage in STAGES},
    }
    state_path.write_text(json.dumps(migrated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--apply-state", action="store_true", help="back up and migrate only .cumcm/state.json")
    args = parser.parse_args()
    root = args.project.resolve()
    if not root.is_dir():
        parser.error(f"project is not a directory: {root}")
    report = analyze(root)
    report_path = args.report or (root / ".cumcm" / "migration-report.json")
    if not report_path.is_absolute():
        report_path = root / report_path
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.apply_state:
        try:
            migrate_state(root)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"state migration failed: {exc}")
            return 2
        print("state migrated; evidence-bearing contracts remain manual")
    print(f"migration report: {report_path}")
    return 1 if any(item["severity"] == "error" for item in report["findings"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
