#!/usr/bin/env python3
"""Append a file-version-bound human decision to .cumcm/decisions.jsonl.

An `accepted` decision derives the stage snapshot. A `revision_requested` decision
is the reopen primitive: it invalidates this stage and every downstream stage so
that iteration never requires hand-editing .cumcm/state.json."""

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


def write_json_atomic(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temp_name = stream.name
    os.replace(temp_name, path)


def reopen(root: Path, stage: str) -> None:
    """Invalidate this stage and everything downstream of it."""
    index = STAGES.index(stage)
    for later in STAGES[index:]:
        (root / ".cumcm" / "snapshots" / f"{later}.json").unlink(missing_ok=True)
    state_path = root / ".cumcm" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    stages = state.get("stages")
    if not isinstance(stages, dict):
        return
    stages[stage] = "needs_revision"
    for later in STAGES[index + 1 :]:
        if stages.get(later) == "passed":
            stages[later] = "needs_revision"
    state["current_stage"] = stage
    write_json_atomic(state_path, state)


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
            "snapshot_version": "0.6.0",
            "project_id": json.loads((root / ".cumcm" / "state.json").read_text(encoding="utf-8")).get("project_id"),
            "stage": args.stage,
            "decision_id": args.decision_id,
            "decision": args.decision,
            "created_at": event["decided_at"],
            "artifacts": scope,
            "snapshot_digest": digest_records(scope),
        }
        write_json_atomic(snapshot_path, snapshot)
    else:
        reopen(root, args.stage)
    print(f"recorded {args.decision_id} for {args.stage}; {len(scope)} artifact(s) bound")
    if args.decision == "revision_requested":
        print(f"reopened {args.stage}; downstream stages are now needs_revision")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
