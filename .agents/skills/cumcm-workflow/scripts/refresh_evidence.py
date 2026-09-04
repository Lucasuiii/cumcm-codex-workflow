#!/usr/bin/env python3
"""Recompute the size/hash metadata that used to be maintained by hand.

This only refreshes observed facts about files that already exist. It never adds,
removes or re-roles an artifact, and it never touches an official source's
declared origin -- an official hash mismatch stays a finding for a human.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from provenance import sha256_file

TARGETS = {
    "sources": "problem/SOURCE_MANIFEST.json",
    "figures": "figures/FIGURE_MANIFEST.json",
    "delivery": "delivery/DELIVERY_MANIFEST.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def write_atomic(path: Path, payload: dict[str, Any]) -> None:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temp_name = stream.name
    os.replace(temp_name, path)


def refresh_entries(root: Path, entries: list[Any], *, hash_key: str = "sha256", only_existing_hash: bool = False) -> int:
    changed = 0
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        target = root / entry["path"]
        if not target.is_file():
            continue
        if only_existing_hash and not entry.get(hash_key):
            continue
        digest = sha256_file(target)
        size = target.stat().st_size
        if entry.get(hash_key) != digest or entry.get("size") != size:
            changed += 1
        entry[hash_key] = digest
        entry["size"] = size
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh size/hash metadata for files already declared in the workspace")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--runs", action="store_true", help="also refresh run manifest input/output metadata")
    args = parser.parse_args()
    root = args.project.resolve()
    if not root.is_dir():
        parser.error(f"project is not a directory: {root}")

    total = 0
    for name, rel in TARGETS.items():
        path = root / rel
        if not path.is_file():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if name == "sources":
            total += refresh_entries(root, data.get("sources", []))
        elif name == "figures":
            total += refresh_entries(root, data.get("figures", []), only_existing_hash=True)
        else:
            total += refresh_entries(root, data.get("files", []), only_existing_hash=True)
        data["updated_at"] = utc_now()
        write_atomic(path, data)
        print(f"refreshed {rel}")

    if args.runs:
        for manifest_path in sorted((root / "runs").glob("*/RUN_MANIFEST.json")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest.get("official_run") is True:
                # An official run's hashes describe a preserved execution. Rewriting them
                # would erase exactly the drift the checker exists to catch.
                print(f"skipped official run {manifest.get('run_id')}; re-record it with record_run.py --rerun instead")
                continue
            total += refresh_entries(root, manifest.get("inputs", []), only_existing_hash=True)
            total += refresh_entries(root, manifest.get("outputs", []), only_existing_hash=True)
            manifest["updated_at"] = utc_now()
            write_atomic(manifest_path, manifest)
            print(f"refreshed {manifest_path.relative_to(root)}")

    print(f"{total} metadata field group(s) updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
