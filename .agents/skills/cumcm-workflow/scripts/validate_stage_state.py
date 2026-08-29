#!/usr/bin/env python3
"""Validate the durable CUMCM workflow state file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


STAGES = ["intake", "problem-analysis", "model-design", "computation", "validation", "paper", "delivery"]
STATUSES = {"not_started", "in_progress", "awaiting_review", "passed", "needs_revision", "blocked"}


def validate(data: object) -> list[str]:
    if not isinstance(data, dict):
        return ["state must be a JSON object"]
    errors = []
    current = data.get("current_stage")
    stages = data.get("stages")
    if current not in STAGES:
        errors.append(f"current_stage must be one of {STAGES}")
    if not isinstance(stages, dict):
        return errors + ["stages must be an object"]
    missing = [stage for stage in STAGES if stage not in stages]
    extra = sorted(set(stages) - set(STAGES))
    if missing:
        errors.append(f"missing stages: {', '.join(missing)}")
    if extra:
        errors.append(f"unknown stages: {', '.join(extra)}")
    for stage, status in stages.items():
        if stage in STAGES and status not in STATUSES:
            errors.append(f"invalid status for {stage}: {status}")
    if current in STAGES and stages.get(current) == "not_started":
        errors.append("current_stage cannot have status not_started")
    if current in STAGES:
        current_index = STAGES.index(current)
        for prior in STAGES[:current_index]:
            if stages.get(prior) != "passed":
                errors.append(f"prior stage must be passed before {current}: {prior}")
        active_later = {"in_progress", "awaiting_review", "passed"}
        for later in STAGES[current_index + 1 :]:
            if stages.get(later) in active_later:
                errors.append(f"later stage cannot be active before {current} passes: {later}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("state", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.state.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid state file: {exc}")
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("state: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
