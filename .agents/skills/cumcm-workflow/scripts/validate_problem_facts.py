#!/usr/bin/env python3
"""Validate traceable problem facts and subproblem contracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def validate(data: object) -> list[str]:
    if not isinstance(data, dict):
        return ["problem facts must be a JSON object"]
    errors = []
    if not str(data.get("problem_id", "")).strip():
        errors.append("problem_id is required")
    sources = data.get("source_files")
    if not isinstance(sources, list) or not sources or not all(isinstance(x, str) and x.strip() for x in sources):
        errors.append("source_files must be a nonempty list of paths")
        sources = []
    subproblems = data.get("subproblems")
    if not isinstance(subproblems, list) or not subproblems:
        errors.append("subproblems must be a nonempty list")
        subproblems = []
    facts = data.get("facts")
    if not isinstance(facts, list) or not facts:
        errors.append("facts must be a nonempty list")
        facts = []
    for label, items, fields in (
        ("subproblem", subproblems, ("id", "request")),
        ("fact", facts, ("id", "statement", "source")),
    ):
        seen = set()
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"{label} {index} must be an object")
                continue
            for field in fields:
                if not str(item.get(field, "")).strip():
                    errors.append(f"{label} {index} missing {field}")
            ident = item.get("id")
            if ident in seen:
                errors.append(f"duplicate {label} id: {ident}")
            seen.add(ident)
            if label == "fact" and isinstance(item.get("source"), str):
                source_file = item["source"].split("#", 1)[0]
                if source_file and source_file not in sources:
                    errors.append(f"fact {ident or index} cites an unregistered source: {source_file}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("facts", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.facts.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid problem facts: {exc}")
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("problem facts: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
