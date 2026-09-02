#!/usr/bin/env python3
"""Choose one official computation backend without creating parity work."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


MATLAB_FEATURES = {
    "numerical_linear_algebra": 3,
    "optimization": 2,
    "ode_pde": 3,
    "signal_processing": 3,
    "control": 3,
}
PYTHON_FEATURES = {
    "data_cleaning": 3,
    "csv_excel": 3,
    "machine_learning": 2,
    "web_data": 4,
    "nlp": 3,
}


def detect_availability() -> dict[str, bool]:
    return {"matlab": shutil.which("matlab") is not None, "python": bool(sys.executable)}


def select_backend(task: dict[str, Any], config: dict[str, Any], availability: dict[str, bool] | None = None) -> dict[str, Any]:
    availability = availability or detect_availability()
    preferred = str(config.get("preferred", "matlab"))
    fallback = str(config.get("fallback", "python"))
    selection = str(config.get("selection", "auto"))
    if preferred not in {"matlab", "python"} or fallback not in {"matlab", "python"}:
        raise ValueError("preferred and fallback must be matlab or python")
    if preferred == fallback:
        raise ValueError("preferred and fallback must be different")
    if selection not in {"auto", "matlab", "python"}:
        raise ValueError("selection must be auto, matlab, or python")

    features = {str(item) for item in task.get("features", [])}
    scores = {"matlab": 0, "python": 0}
    reasons: dict[str, list[str]] = {"matlab": [], "python": []}
    for feature in sorted(features):
        if feature in MATLAB_FEATURES:
            scores["matlab"] += MATLAB_FEATURES[feature]
            reasons["matlab"].append(feature)
        if feature in PYTHON_FEATURES:
            scores["python"] += PYTHON_FEATURES[feature]
            reasons["python"].append(feature)
    existing = task.get("existing_code")
    if existing in scores:
        scores[str(existing)] += 5
        reasons[str(existing)].append("existing_code")
    required = task.get("required_backend")
    if required in scores:
        scores[str(required)] += 100
        reasons[str(required)].append("required_backend")
    scores[preferred] += 1
    reasons[preferred].append("configured_preference_tiebreak")

    desired = selection if selection != "auto" else max(scores, key=lambda name: (scores[name], name == preferred))
    fallback_from = None
    if not availability.get(desired, False):
        alternative = fallback if desired == preferred else preferred
        if not availability.get(alternative, False):
            raise ValueError("no reliable MATLAB or Python runtime is available")
        fallback_from = desired
        desired = alternative

    rationale_parts = []
    if reasons[desired]:
        rationale_parts.append("fit: " + ", ".join(reasons[desired]))
    rationale_parts.append(f"score matlab={scores['matlab']}, python={scores['python']}")
    if fallback_from:
        rationale_parts.append(f"fallback from unavailable {fallback_from}")
    return {
        "selected_language": desired,
        "selection_rationale": "; ".join(rationale_parts),
        "fallback_from": fallback_from,
        "scores": scores,
        "availability": {"matlab": bool(availability.get("matlab")), "python": bool(availability.get("python"))},
        "single_backend_policy": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Select one MATLAB or Python backend for a CUMCM computation task")
    parser.add_argument("--task", type=Path, required=True, help="JSON task features")
    parser.add_argument("--config", type=Path, required=True, help="JSON implementation preference")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        task = json.loads(args.task.read_text(encoding="utf-8"))
        config = json.loads(args.config.read_text(encoding="utf-8"))
        result = select_backend(task, config)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
