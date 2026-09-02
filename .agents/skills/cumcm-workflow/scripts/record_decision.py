#!/usr/bin/env python3
"""Append a file-version-bound human decision to .cumcm/decisions.jsonl."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from workflow_checks import STAGES, safe_project_path, sha256, stage_scope_paths
from provenance import digest_records


def load_events(path: Path) -> list[dict]:
    if not path.exists():
        return []
    events: list[dict] = []
    seen: set[str] = set()
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        event = json.loads(raw)
        if not isinstance(event, dict):
            raise ValueError(f"line {line_number} is not an object")
        decision_id = event.get("decision_id")
        if not isinstance(decision_id, str) or not decision_id or decision_id in seen:
            raise ValueError(f"line {line_number} has a missing or duplicate decision_id")
        seen.add(decision_id)
        events.append(event)
    return events


def main() -> int:
    parser = argparse.ArgumentParser(description="Record an append-only, artifact-bound workflow decision")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--stage", required=True, choices=STAGES)
    parser.add_argument("--decision", required=True, choices=("accepted", "revision_requested"))
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--reviewer", required=True)
    parser.add_argument("--task-turn-ref", required=True)
    parser.add_argument("--summary", required=True, dest="user_visible_summary")
    parser.add_argument("--scope", action="append", default=[], help="project-relative file; repeat to override the stage defaults")
    args = parser.parse_args()

    root = args.project.resolve()
    if not root.is_dir():
        parser.error(f"project is not a directory: {root}")
    log_path = root / ".cumcm" / "decisions.jsonl"
    events = load_events(log_path)
    if args.decision_id in {event["decision_id"] for event in events}:
        parser.error(f"decision_id already exists: {args.decision_id}")

    scope_paths = args.scope or stage_scope_paths(root, args.stage)
    if ".cumcm/state.json" in scope_paths:
        parser.error("workflow state is mutable and must not be included in a decision scope")
    scope = []
    for rel in scope_paths:
        artifact = safe_project_path(root, rel)
        if artifact is None or not artifact.is_file():
            parser.error(f"scope file is missing or unsafe: {rel}")
        scope.append({"path": rel, "sha256": sha256(artifact)})

    event = {
        "decision_id": args.decision_id,
        "stage": args.stage,
        "decision": args.decision,
        "scope": scope,
        "reviewer": args.reviewer,
        "task_turn_ref": args.task_turn_ref,
        "user_visible_summary": args.user_visible_summary,
        "decided_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    snapshot_path = root / ".cumcm" / "snapshots" / f"{args.stage}.json"
    if args.decision == "accepted":
        snapshot = {
            "snapshot_version": "0.5.0",
            "project_id": json.loads((root / ".cumcm" / "state.json").read_text(encoding="utf-8")).get("project_id"),
            "stage": args.stage,
            "decision_id": args.decision_id,
            "decision": args.decision,
            "created_at": event["decided_at"],
            "artifacts": scope,
            "snapshot_digest": digest_records(scope),
        }
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=snapshot_path.parent, delete=False) as stream:
            json.dump(snapshot, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            temp_name = stream.name
        os.replace(temp_name, snapshot_path)
    else:
        snapshot_path.unlink(missing_ok=True)
    print(f"recorded {args.decision_id} for {args.stage}; {len(scope)} artifact(s) bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
