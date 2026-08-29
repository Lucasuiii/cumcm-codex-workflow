#!/usr/bin/env python3
"""Validate that a run manifest describes a completed execution and real outputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REQUIRED = ("run_id", "command", "status", "started_at", "finished_at", "exit_code", "inputs", "outputs")


def validate(data: object, root: Path) -> list[str]:
    if not isinstance(data, dict):
        return ["run manifest must be a JSON object"]
    errors = [f"missing field: {field}" for field in REQUIRED if field not in data]
    if data.get("status") != "completed":
        errors.append("status must be completed")
    if data.get("exit_code") != 0:
        errors.append("exit_code must be 0")
    outputs = data.get("outputs")
    if not isinstance(outputs, list) or not outputs:
        errors.append("outputs must be a nonempty list")
    else:
        for rel in outputs:
            if not isinstance(rel, str) or not rel.strip():
                errors.append("every output must be a relative path")
                continue
            path = (root / rel).resolve()
            try:
                path.relative_to(root.resolve())
            except ValueError:
                errors.append(f"output escapes project root: {rel}")
                continue
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f"missing or empty output: {rel}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid run manifest: {exc}")
        return 2
    errors = validate(data, args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("run manifest: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
