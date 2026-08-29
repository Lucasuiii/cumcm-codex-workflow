#!/usr/bin/env python3
"""Validate claim statuses and their links to local evidence artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


STATUSES = {"supported", "partially_supported", "contradicted", "missing_evidence", "ambiguous"}


def validate(data: object, root: Path) -> list[str]:
    if not isinstance(data, dict) or not isinstance(data.get("claims"), list):
        return ["claim ledger must contain a claims list"]
    errors = []
    seen = set()
    for index, claim in enumerate(data["claims"]):
        if not isinstance(claim, dict):
            errors.append(f"claim {index} must be an object")
            continue
        ident = str(claim.get("id", "")).strip()
        text = str(claim.get("claim", "")).strip()
        status = claim.get("status")
        evidence = claim.get("evidence", [])
        if not ident:
            errors.append(f"claim {index} missing id")
        elif ident in seen:
            errors.append(f"duplicate claim id: {ident}")
        seen.add(ident)
        if not text:
            errors.append(f"claim {ident or index} missing claim text")
        if status not in STATUSES:
            errors.append(f"claim {ident or index} has invalid status: {status}")
        if status in {"supported", "partially_supported"} and not evidence:
            errors.append(f"claim {ident or index} requires evidence")
        if not isinstance(evidence, list):
            errors.append(f"claim {ident or index} evidence must be a list")
            continue
        for rel in evidence:
            path = (root / rel).resolve() if isinstance(rel, str) else None
            if path is None:
                errors.append(f"claim {ident or index} has a non-path evidence item")
                continue
            try:
                path.relative_to(root.resolve())
            except ValueError:
                errors.append(f"claim {ident or index} evidence escapes root: {rel}")
                continue
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f"claim {ident or index} missing evidence: {rel}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        data = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid claim ledger: {exc}")
        return 2
    errors = validate(data, args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("claim ledger: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
