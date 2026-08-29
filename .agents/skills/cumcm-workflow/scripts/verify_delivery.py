#!/usr/bin/env python3
"""Verify final delivery files and optional SHA-256 hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(data: object, root: Path) -> list[str]:
    if not isinstance(data, dict) or not isinstance(data.get("files"), list):
        return ["delivery manifest must contain a files list"]
    errors = []
    for index, item in enumerate(data["files"]):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            errors.append(f"delivery item {index} requires a path")
            continue
        rel = item["path"]
        path = (root / rel).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"delivery path escapes root: {rel}")
            continue
        if not path.is_file() or path.stat().st_size == 0:
            errors.append(f"missing or empty delivery file: {rel}")
            continue
        expected = item.get("sha256")
        if expected and sha256(path) != expected:
            errors.append(f"hash mismatch: {rel}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        data = json.loads(args.manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid delivery manifest: {exc}")
        return 2
    errors = validate(data, args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("delivery manifest: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
