#!/usr/bin/env python3
"""Copy a v0.4 workspace into a conservative v0.5 working-mode workspace."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from provenance import digest_records, sha256_file, tree_snapshot


OLD_VERSION = "0.4.0"
NEW_VERSION = "0.5.0"


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def infer_language(run: dict[str, Any]) -> str:
    command = " ".join(str(value) for value in run.get("argv", [])).casefold()
    return "matlab" if "matlab" in command else "python"


def capability_entrypoints(root: Path) -> dict[str, list[str]]:
    path = root / "analysis" / "TASK_CAPABILITIES.json"
    if not path.is_file():
        return {}
    data = read_json(path)
    return {
        str(item.get("capability_id")): [str(value).split(":", 1)[0] for value in item.get("code_entry_points", [])]
        for item in data.get("capabilities", []) if isinstance(item, dict)
    }


def update_review_contracts(root: Path) -> None:
    package_path = root / "validation" / "independent-review-package" / "REVIEW_PACKAGE_MANIFEST.json"
    if not package_path.is_file():
        return
    package = read_json(package_path)
    records = []
    for item in package.get("files", []):
        if not isinstance(item, dict):
            continue
        packaged = root / str(item.get("path"))
        if not packaged.is_file():
            continue
        item["sha256"] = sha256_file(packaged)
        marker = "validation/independent-review-package/materials/"
        if str(item.get("path", "")).startswith(marker):
            source_path = str(item["path"])[len(marker):]
            if (root / source_path).is_file():
                item["source_path"] = source_path
        records.append(item)
    digest_input = [
        {"path": item["path"], "sha256": item["sha256"]}
        for item in records if not str(item["path"]).endswith("INDEPENDENT_REVIEW_RESULT_TEMPLATE.json")
    ]
    upstream = [
        {"path": item["source_path"], "sha256": item["sha256"]}
        for item in records if item.get("source_path")
    ]
    package.update({
        "review_mode": "full",
        "previous_review_path": None,
        "target_finding_ids": [],
        "package_digest": digest_records(digest_input),
        "upstream_digest": digest_records(upstream) if upstream else "0" * 64,
    })
    write_json(package_path, package)
    result_path = root / "validation" / "INDEPENDENT_REVIEW_RESULT.json"
    if result_path.is_file():
        result = read_json(result_path)
        verdicts = {"accepted": "accepted", "revision_requested": "revision_required", "inconclusive": "inconclusive"}
        severities = {"fatal": "P0", "major": "P1", "minor": "P2"}
        result.update({
            "review_id": result.get("review_id", "MIGRATED-V04-REVIEW"),
            "package_digest": package["package_digest"],
            "review_mode": "full",
            "previous_review_path": None,
            "target_finding_ids": [],
            "verdict": verdicts.get(result.get("verdict"), "inconclusive"),
        })
        for item in result.get("findings", []):
            if isinstance(item, dict):
                item["severity"] = severities.get(item.get("severity"), "P1")
                item["status"] = "open"
        write_json(result_path, result)


def update_paper_contracts(root: Path) -> None:
    plan_path = root / "paper" / "PAPER_PLAN.json"
    if plan_path.is_file():
        plan = read_json(plan_path)
        plan.setdefault("claim_selection", [
            {"claim_id": item.get("claim_id"), "subproblem_id": item.get("subproblem_id"), "purpose": "migrated from v0.4 claims-evidence matrix"}
            for item in plan.get("claims_evidence_matrix", []) if isinstance(item, dict)
        ])
        plan.setdefault("representation_plan", [
            {"item_id": item.get("figure_id", f"MIGRATED-{index}"), "claim_ids": item.get("claim_ids", []), "result_ids": item.get("result_ids", []), "medium": "figure" if item.get("kind") != "table" else "table", "purpose": item.get("purpose", "migrated representation"), "artifact_id": item.get("figure_id")}
            for index, item in enumerate(plan.get("figure_plan", []), 1) if isinstance(item, dict)
        ])
        plan.setdefault("paper_structure", [
            {"section_id": f"MIGRATED-{index}", "title": str(item.get("subproblem_id")), "purpose": "answer the subproblem", "subproblem_ids": [item.get("subproblem_id")], "claim_ids": [row.get("claim_id") for row in plan.get("claims_evidence_matrix", []) if isinstance(row, dict) and row.get("subproblem_id") == item.get("subproblem_id")]}
            for index, item in enumerate(plan.get("question_argument_chains", []), 1) if isinstance(item, dict)
        ])
        write_json(plan_path, plan)
    quality_path = root / "paper" / "PAPER_QUALITY_REPORT.json"
    if quality_path.is_file():
        quality = read_json(quality_path)
        content = quality.get("content_review")
        if isinstance(content, dict):
            content.setdefault("summary", "Migrated v0.4 content review; recheck before final delivery.")
            for question in content.get("questions", []):
                if isinstance(question, dict):
                    question.setdefault("status", "pass")
                    question.setdefault("notes", "Migrated v0.4 question review.")
        write_json(quality_path, quality)
    receipt_path = root / "delivery" / "COMPILE_RECEIPT.json"
    latex_path = root / "paper" / "LATEX_TEMPLATE_MANIFEST.json"
    if receipt_path.is_file() and latex_path.is_file():
        receipt = read_json(receipt_path)
        latex = read_json(latex_path)
        files = [str(value) for value in latex.get("required_files", []) if (root / str(value)).is_file()]
        if files:
            receipt["source_snapshot"] = tree_snapshot(root, files, entrypoint=str(latex.get("main_path")))
        write_json(receipt_path, receipt)


def migrate(source: Path, target: Path) -> Path:
    source = source.resolve()
    target = target.resolve(strict=False)
    if not source.is_dir():
        raise ValueError(f"source workspace is missing: {source}")
    state = read_json(source / ".cumcm" / "state.json")
    if state.get("workflow_version") != OLD_VERSION:
        raise ValueError("migration accepts only a v0.4 workspace")
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        raise ValueError(f"target must be new or empty: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{target.name}.migrate-", dir=target.parent) as temp:
        staging = Path(temp) / "workspace"
        shutil.copytree(source, staging, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".cumcm/tmp"))
        entries = capability_entrypoints(staging)
        for path in staging.rglob("*.json"):
            try:
                data = read_json(path)
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if data.get("schema_version") == OLD_VERSION:
                data["schema_version"] = NEW_VERSION
            producer = data.get("producer")
            if isinstance(producer, dict) and producer.get("version") == OLD_VERSION:
                producer["version"] = NEW_VERSION
            if data.get("artifact_type") == "workflow_state":
                data.update({"workflow_version": NEW_VERSION, "mode": "working", "implementation": {"preferred": "matlab", "fallback": "python", "selection": "auto"}})
            if data.get("artifact_type") == "run_manifest":
                language = infer_language(data)
                source_files = sorted({rel for cap in data.get("capability_ids", []) for rel in entries.get(str(cap), []) if (staging / rel).is_file()})
                if source_files:
                    snapshot = tree_snapshot(staging, source_files)
                else:
                    placeholder = str(data.get("stdout_path"))
                    snapshot = tree_snapshot(staging, [placeholder])
                data["official_run"] = False
                data["implementation"] = {
                    "selected_language": language,
                    "selection_rationale": "migrated from v0.4; rerun required before claim use",
                    "entry_point": source_files[0] if source_files else placeholder,
                    "runtime": "migrated_unverified",
                    "dependencies": [],
                    "matlab_toolboxes": [],
                    "fallback_from": None,
                    "source_snapshot": snapshot,
                }
            write_json(path, data)
        update_review_contracts(staging)
        update_paper_contracts(staging)
        (staging / ".cumcm" / "snapshots").mkdir(parents=True, exist_ok=True)
        (staging / "handoffs").mkdir(parents=True, exist_ok=True)
        migration = {
            "from": OLD_VERSION,
            "to": NEW_VERSION,
            "mode": "working",
            "official_runs_recertified": False,
            "next_action": "select one backend and rerun claim-bearing computation before finalizing",
        }
        write_json(staging / ".cumcm" / "migration-report.json", migration)
        if target.exists():
            target.rmdir()
        shutil.move(staging, target)
    return target / ".cumcm" / "migration-report.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Copy a v0.4 CUMCM workspace into a v0.5 working workspace")
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--target", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = migrate(args.source, args.target)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    print(f"migrated workspace: {report}")
    print("claim-bearing runs remain non-official until one selected backend is rerun successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
