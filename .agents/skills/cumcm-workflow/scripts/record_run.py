#!/usr/bin/env python3
"""Execute a computation and record every machine fact about it.

The agent declares meaning on the command line (purpose, capabilities, which files
are formal inputs or claim-bearing outputs). Everything else -- argv, timings, exit
status, logs, hashes, and the source-tree snapshot -- is observed, never typed.

A rerun never overwrites: it appends a new run whose `parent_run_id` points at
the one it replaces, and the declared source and outputs are frozen into the run
directory so a preserved run stays verifiable no matter what the workspace does
next.

Exploratory runs are deliberately cheap:

    record_run.py --project P -- python3 code/try.py

Freezing a run for formal results costs a few declarations:

    record_run.py --project P --official --capability CAP-Q1-001 \
        --source code/solve.py --input data/q1.csv:formal \
        --output runs/out/q1.json:claim -- python3 code/solve.py
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from provenance import sha256_file, tree_snapshot

WORKFLOW_VERSION = "0.6.0"
INPUT_ROLES = {"formal": "formal_input", "auxiliary": "auxiliary_input"}
OUTPUT_ROLES = {"claim": "claim_bearing_output", "intermediate": "intermediate_output", "diagnostic": "diagnostic_output"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def relative(root: Path, value: str) -> str:
    candidate = (root / value).resolve() if not Path(value).is_absolute() else Path(value).resolve()
    try:
        return candidate.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise SystemExit(f"path escapes the project: {value}") from exc


def split_role(spec: str, table: dict[str, str], default: str) -> tuple[str, str]:
    path, _, role = spec.partition(":")
    if not role:
        return path, default
    if role not in table:
        raise SystemExit(f"unknown role '{role}'; expected one of {', '.join(sorted(table))}")
    return path, table[role]


def file_record(root: Path, rel: str, role: str) -> dict[str, Any]:
    target = root / rel
    if not target.is_file():
        raise SystemExit(f"declared file does not exist after the run: {rel}")
    return {
        "path": rel,
        "sha256": sha256_file(target),
        "size": target.stat().st_size,
        "media_type": mimetypes.guess_type(target.name)[0] or "application/octet-stream",
        "evidence_role": role,
    }


def infer_language(argv: list[str], explicit: str | None) -> str:
    if explicit:
        return explicit
    joined = " ".join(argv).casefold()
    if "matlab" in joined:
        return "matlab"
    if "python" in joined or joined.endswith(".py"):
        return "python"
    raise SystemExit("cannot infer the backend from the command; pass --language matlab|python")


def infer_entry_point(root: Path, argv: list[str], sources: list[str]) -> str:
    for token in argv[1:]:
        stripped = token.split(":", 1)[0]
        if stripped.endswith((".py", ".m")) and (root / stripped).is_file():
            return relative(root, stripped)
    if sources:
        return sources[0]
    raise SystemExit("cannot infer the entry point; pass --source <file>")


def runtime_label(language: str, argv: list[str]) -> str:
    if language == "python":
        return f"Python {platform.python_version()} ({sys.executable})"
    executable = next((token for token in argv if "matlab" in token.casefold()), "matlab")
    return f"MATLAB via {executable}"


def parse_assertions(entries: list[str], assertion_file: str | None, root: Path) -> list[dict[str, Any]]:
    assertions: list[dict[str, Any]] = []
    for entry in entries:
        name, _, verdict = entry.partition("=")
        name = name.strip()
        if not name:
            raise SystemExit(f"malformed --assert entry: {entry}")
        passed = verdict.strip().casefold() not in {"fail", "false", "0", "no"}
        assertions.append({"name": name, "passed": passed})
    if assertion_file:
        payload = json.loads((root / assertion_file).read_text(encoding="utf-8"))
        items = payload.get("assertions") if isinstance(payload, dict) else payload
        for item in items or []:
            if isinstance(item, dict) and item.get("name"):
                assertions.append({"name": str(item["name"]), "passed": item.get("passed") is True, **{k: v for k, v in item.items() if k not in {"name", "passed"}}})
    return assertions


def freeze(root: Path, run_dir: Path, rel: str, kind: str) -> str:
    """Copy an artifact into the run directory and return its frozen path.

    The frozen tree mirrors the original layout (runs/<id>/source/code/solve.py),
    so the live counterpart of any frozen file is just the path with the
    runs/<id>/<kind>/ prefix removed. That keeps drift detection possible without
    storing a second mapping.
    """
    origin = root / rel
    if not origin.is_file():
        raise SystemExit(f"declared file does not exist after the run: {rel}")
    destination = run_dir / kind / rel
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origin, destination)
    return destination.relative_to(root).as_posix()


def live_path_of(frozen: str) -> str | None:
    """Inverse of freeze(): runs/<id>/source/code/solve.py -> code/solve.py."""
    parts = frozen.split("/")
    if len(parts) > 3 and parts[0] == "runs" and parts[2] in {"source", "outputs"}:
        return "/".join(parts[3:])
    return None


def child_run_id(root: Path, parent: str) -> str:
    """RUN-Q1-001 -> RUN-Q1-002, keeping whatever prefix the parent used."""
    existing = {path.parent.name for path in (root / "runs").glob("*/RUN_MANIFEST.json")}
    match = re.match(r"^(.*?)(\d+)$", parent)
    if match:
        head, number = match.group(1), int(match.group(2))
        width = len(match.group(2))
        while True:
            number += 1
            candidate = f"{head}{number:0{width}d}"
            if candidate not in existing:
                return candidate
    index = 2
    while f"{parent}-R{index}" in existing:
        index += 1
    return f"{parent}-R{index}"


def load_previous(root: Path, run_id: str) -> dict[str, Any]:
    path = root / "runs" / run_id / "RUN_MANIFEST.json"
    if not path.is_file():
        raise SystemExit(f"cannot rerun unknown run: {run_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def next_run_id(root: Path) -> str:
    existing = {path.parent.name for path in (root / "runs").glob("*/RUN_MANIFEST.json")} if (root / "runs").is_dir() else set()
    index = 1
    while f"RUN-{index:03d}" in existing:
        index += 1
    return f"RUN-{index:03d}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a command and record its evidence; the agent never types a hash")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--run-id")
    parser.add_argument("--rerun", help="re-execute an existing run's exact argv as a new, appended run")
    parser.add_argument("--purpose")
    parser.add_argument("--capability", action="append", default=[])
    parser.add_argument("--candidate", action="append", default=[], help="model candidate this run evaluates; repeat as needed")
    parser.add_argument("--source", action="append", default=[], help="project-relative source file that the snapshot must cover")
    parser.add_argument("--input", action="append", default=[], help="path[:formal|auxiliary]")
    parser.add_argument("--output", action="append", default=[], help="path[:claim|intermediate|diagnostic]")
    parser.add_argument("--assert", dest="assertions", action="append", default=[], help="NAME=pass|fail")
    parser.add_argument("--assert-file", help="project-relative JSON file the run wrote with its own assertions")
    parser.add_argument("--dependency", action="append", default=[])
    parser.add_argument("--toolbox", action="append", default=[])
    parser.add_argument("--language", choices=("matlab", "python"))
    parser.add_argument("--rationale")
    parser.add_argument("--official", action="store_true")
    parser.add_argument("--timeout", type=float)
    parser.add_argument("command", nargs=argparse.REMAINDER, help="-- followed by the command to execute")
    args = parser.parse_args()

    root = args.project.resolve()
    if not root.is_dir():
        parser.error(f"project is not a directory: {root}")

    command = [token for token in args.command if token != "--"]
    previous: dict[str, Any] = {}
    run_id = args.run_id
    if args.rerun:
        previous = load_previous(root, args.rerun)
        # A rerun appends. Overwriting the parent would destroy the only record of
        # what the superseded run executed and produced.
        run_id = run_id or child_run_id(root, args.rerun)
        if run_id == args.rerun:
            parser.error("a rerun must use a new run id; it never overwrites its parent")
        command = command or [str(token) for token in previous.get("argv", [])]
    if not command:
        parser.error("provide the command to execute after --")
    run_id = run_id or next_run_id(root)

    capabilities = args.capability or [str(value) for value in previous.get("capability_ids", [])]
    candidates = args.candidate or [str(value) for value in previous.get("candidate_ids", [])]
    sources = [relative(root, value) for value in args.source]
    if not sources and previous:
        snapshot = previous.get("implementation", {}).get("source_snapshot", {})
        sources = [live_path_of(str(value)) or str(value) for value in snapshot.get("files", [])]
    declared_inputs = args.input or [
        f"{item['path']}:{'formal' if item.get('evidence_role') == 'formal_input' else 'auxiliary'}"
        for item in previous.get("inputs", []) if isinstance(item, dict)
    ]
    declared_outputs = args.output or [
        f"{live_path_of(str(item['path'])) or item['path']}:"
        f"{ {'claim_bearing_output': 'claim', 'intermediate_output': 'intermediate'}.get(item.get('evidence_role'), 'diagnostic') }"
        for item in previous.get("outputs", []) if isinstance(item, dict)
    ]

    language = infer_language(command, args.language or previous.get("implementation", {}).get("selected_language"))
    entry_point = infer_entry_point(root, command, sources)
    if entry_point not in sources:
        sources.append(entry_point)

    run_dir = root / "runs" / run_id
    if (run_dir / "RUN_MANIFEST.json").is_file():
        parser.error(f"run {run_id} already exists; runs are append-only, use --rerun {run_id}")
    run_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"

    started_at = utc_now()
    try:
        with stdout_path.open("w", encoding="utf-8") as out, stderr_path.open("w", encoding="utf-8") as err:
            completed = subprocess.run(command, cwd=root, stdout=out, stderr=err, timeout=args.timeout, check=False)
        exit_code = completed.returncode
        status = "completed" if exit_code == 0 else "failed"
    except subprocess.TimeoutExpired:
        exit_code = 124
        status = "interrupted"
    except FileNotFoundError as exc:
        parser.error(f"cannot execute the command: {exc}")
    finished_at = utc_now()

    official = args.official
    if official and status != "completed":
        print(f"run {run_id} exited {exit_code}; recording it as exploratory instead of official", file=sys.stderr)
        official = False
    if official and not capabilities:
        parser.error("an official run must name at least one --capability")

    # Inputs are hashed where they live: official material is immutable by intake
    # contract, and a changed team input is drift worth seeing.
    inputs = [file_record(root, relative(root, spec.split(":", 1)[0]), role)
              for spec, role in ((s, split_role(s, INPUT_ROLES, "auxiliary_input")[1]) for s in declared_inputs)]
    # Source and outputs are frozen: a rerun would otherwise overwrite exactly the
    # files this run's evidence points at.
    frozen_sources = [freeze(root, run_dir, rel, "source") for rel in sources]
    frozen_entry_point = freeze(root, run_dir, entry_point, "source")
    outputs = [
        file_record(root, freeze(root, run_dir, relative(root, spec.split(":", 1)[0]), "outputs"), role)
        for spec, role in ((s, split_role(s, OUTPUT_ROLES, "diagnostic_output")[1]) for s in declared_outputs)
    ]
    if not outputs:
        # Every run produces at least its own log; recording it keeps a zero-flag
        # exploratory run schema-valid without inventing a claim-bearing artifact.
        outputs = [file_record(root, stdout_path.relative_to(root).as_posix(), "diagnostic_output")]
    if official and not any(item["evidence_role"] == "claim_bearing_output" for item in outputs):
        parser.error("an official run must declare at least one --output <path>:claim")

    manifest = {
        "schema_version": WORKFLOW_VERSION,
        "artifact_type": "run_manifest",
        "project_id": json.loads((root / ".cumcm" / "state.json").read_text(encoding="utf-8"))["project_id"],
        "updated_at": finished_at,
        "producer": {"kind": "script", "name": "record_run.py", "version": WORKFLOW_VERSION},
        "run_id": run_id,
        "purpose": args.purpose or previous.get("purpose") or ("official computation" if official else "exploratory run"),
        "capability_ids": capabilities,
        "candidate_ids": candidates,
        "argv": command,
        "working_directory": ".",
        "started_at": started_at,
        "finished_at": finished_at,
        "exit_code": exit_code,
        "status": status,
        "official_run": official,
        "implementation": {
            "selected_language": language,
            "selection_rationale": args.rationale or previous.get("implementation", {}).get("selection_rationale") or f"recorded by record_run.py from the executed {language} command",
            "entry_point": frozen_entry_point,
            "runtime": runtime_label(language, command),
            "dependencies": args.dependency or [str(value) for value in previous.get("implementation", {}).get("dependencies", [])],
            "matlab_toolboxes": args.toolbox,
            "fallback_from": None,
            "source_snapshot": tree_snapshot(root, frozen_sources, entrypoint=frozen_entry_point),
        },
        "inputs": inputs,
        "outputs": outputs,
        "environment": {"platform": platform.platform(), "python": platform.python_version()},
        "stdout_path": stdout_path.relative_to(root).as_posix(),
        "stderr_path": stderr_path.relative_to(root).as_posix(),
        "assertions": parse_assertions(args.assertions, args.assert_file, root) or previous.get("assertions", []),
        "parent_run_id": args.rerun or None,
    }
    destination = run_dir / "RUN_MANIFEST.json"
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=run_dir, delete=False) as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
        temp_name = stream.name
    os.replace(temp_name, destination)

    grade = "official" if official else "exploratory"
    print(f"recorded {grade} run {run_id} (exit {exit_code}) -> {destination.relative_to(root)}")
    if args.rerun:
        print(f"appended after {args.rerun}; that run and its evidence are untouched")
    for entry in outputs:
        if entry["evidence_role"] == "claim_bearing_output":
            print(f"claim-bearing output frozen at {entry['path']}")
    if candidates:
        print(f"evaluated candidate(s): {', '.join(candidates)} -- cite this run in the candidate's evaluation_run_ids")
    if not official:
        print("exploratory runs never support formal results; add --official once the command is the one you mean to cite")
    return 0 if status == "completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
