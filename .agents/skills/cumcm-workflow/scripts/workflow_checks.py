#!/usr/bin/env python3
"""Deterministic v0.2 contract and cross-artifact checks.

The checks in this module establish structure, provenance, recorded execution,
and declared relationships. They do not establish mathematical correctness.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator
from referencing import Registry, Resource


STAGES = [
    "intake",
    "problem-analysis",
    "model-design",
    "computation",
    "validation",
    "paper",
    "delivery",
]
STAGE_STATUSES = {
    "not_started",
    "in_progress",
    "awaiting_review",
    "passed",
    "needs_revision",
    "blocked",
}
EVIDENCE_STATES = {
    "not_checked",
    "missing_evidence",
    "supported_not_reproduced",
    "reproduced",
    "partially_supported",
    "contradicted",
    "ambiguous",
    "not_applicable",
}
REVIEW_DECISIONS = {"unreviewed", "accepted", "revision_requested"}
PROFILES = {"strict", "sprint"}

CONTRACT_PATHS = {
    "state": ".cumcm/state.json",
    "sources": "problem/SOURCE_MANIFEST.json",
    "facts": "analysis/PROBLEM_FACTS.json",
    "capabilities": "analysis/TASK_CAPABILITIES.json",
    "model": "model/MODEL_CONTRACT.json",
    "cross_question": "model/CROSS_QUESTION_LEDGER.json",
    "results": "results/RESULTS_INDEX.json",
    "claims": "validation/CLAIM_LEDGER.json",
    "figures": "figures/FIGURE_MANIFEST.json",
    "delivery": "delivery/DELIVERY_MANIFEST.json",
}

STAGE_CONTRACTS = {
    "intake": ("state", "sources"),
    "problem-analysis": ("state", "sources", "facts", "capabilities"),
    "model-design": (
        "state",
        "sources",
        "facts",
        "capabilities",
        "model",
        "cross_question",
    ),
    "computation": (
        "state",
        "sources",
        "facts",
        "capabilities",
        "model",
        "cross_question",
        "results",
    ),
    "validation": tuple(CONTRACT_PATHS)[:8],
    "paper": tuple(CONTRACT_PATHS)[:-1],
    "delivery": tuple(CONTRACT_PATHS),
}

SCHEMA_FILES = {
    "state": "workflow-state.schema.json",
    "sources": "source-manifest.schema.json",
    "facts": "problem-facts.schema.json",
    "capabilities": "task-capabilities.schema.json",
    "model": "model-contract.schema.json",
    "cross_question": "cross-question-ledger.schema.json",
    "results": "results-index.schema.json",
    "claims": "claim-ledger.schema.json",
    "figures": "figure-manifest.schema.json",
    "delivery": "delivery-manifest.schema.json",
    "run": "run-manifest.schema.json",
}

STRONG_CLAIM_PATTERNS = {
    "global_optimality": re.compile(r"\bglobal(?:ly)? optimal\b|全局最优", re.I),
    "unbiasedness": re.compile(r"\bunbiased\b|无偏", re.I),
    "equivalence": re.compile(r"\bequivalent\b|统计等价|等价", re.I),
    "causality": re.compile(r"\bcausal(?:ity)?\b|因果", re.I),
    "robustness": re.compile(r"\brobust(?:ness)?\b|鲁棒", re.I),
}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    evidence_type: str
    owning_stage: str
    path: str
    message: str
    pointer: str = ""
    related_ids: list[str] = field(default_factory=list)
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def finding(
    rule_id: str,
    severity: str,
    evidence_type: str,
    stage: str,
    path: str,
    message: str,
    *,
    pointer: str = "",
    related_ids: Iterable[str] = (),
    remediation: str = "",
) -> Finding:
    return Finding(
        rule_id=rule_id,
        severity=severity,
        evidence_type=evidence_type,
        owning_stage=stage,
        path=path,
        message=message,
        pointer=pointer,
        related_ids=list(related_ids),
        remediation=remediation,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_project_path(root: Path, rel: Any) -> Path | None:
    if not isinstance(rel, str) or not rel.strip():
        return None
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def read_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)


def check_schema(data: Any, schema_name: str, stage: str, path: str) -> list[Finding]:
    schema_dir = Path(__file__).resolve().parents[1] / "schemas"
    schema_path = schema_dir / SCHEMA_FILES[schema_name]
    schema, error = read_json(schema_path)
    if error:
        return [finding("SCHEMA-E001", "error", "structural", stage, path, f"cannot load schema: {error}")]
    common_path = schema_dir / "common.schema.json"
    common, common_error = read_json(common_path)
    if common_error:
        return [finding("SCHEMA-E001", "error", "structural", stage, path, f"cannot load common schema: {common_error}")]
    common_resource = Resource.from_contents(common)
    registry = Registry().with_resource(common_path.as_uri(), common_resource)
    registry = registry.with_resource(common.get("$id", common_path.as_uri()), common_resource)
    validator = Draft202012Validator(schema, registry=registry)
    findings: list[Finding] = []
    for issue in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path)):
        pointer = "" if not issue.absolute_path else "/" + "/".join(str(part) for part in issue.absolute_path)
        findings.append(
            finding(
                "SCHEMA-E002",
                "error",
                "structural",
                stage,
                path,
                issue.message,
                pointer=pointer,
            )
        )
    return findings


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def item_id(item: Any, *keys: str) -> str:
    if not isinstance(item, dict):
        return ""
    for key in keys:
        value = item.get(key)
        if nonempty(value):
            return value.strip()
    return ""


def ids(items: Any, *keys: str) -> set[str]:
    return {ident for item in as_list(items) if (ident := item_id(item, *keys))}


def require_fields(
    items: Any,
    fields: tuple[str, ...],
    id_keys: tuple[str, ...],
    prefix: str,
    stage: str,
    path: str,
) -> list[Finding]:
    findings: list[Finding] = []
    if not isinstance(items, list):
        return [finding(f"{prefix}-E001", "error", "structural", stage, path, "expected a list")]
    seen: set[str] = set()
    for index, item in enumerate(items):
        pointer = f"/{index}"
        if not isinstance(item, dict):
            findings.append(
                finding(f"{prefix}-E002", "error", "structural", stage, path, "item must be an object", pointer=pointer)
            )
            continue
        ident = item_id(item, *id_keys)
        if not ident:
            findings.append(
                finding(f"{prefix}-E003", "error", "structural", stage, path, "item has no stable ID", pointer=pointer)
            )
        elif ident in seen:
            findings.append(
                finding(
                    f"{prefix}-E004",
                    "error",
                    "structural",
                    stage,
                    path,
                    f"duplicate ID: {ident}",
                    pointer=pointer,
                    related_ids=[ident],
                )
            )
        seen.add(ident)
        for name in fields:
            value = item.get(name)
            if value is None or value == "" or value == []:
                findings.append(
                    finding(
                        f"{prefix}-E005",
                        "error",
                        "structural",
                        stage,
                        path,
                        f"{ident or f'item {index}'} missing {name}",
                        pointer=f"{pointer}/{name}",
                        related_ids=[ident] if ident else [],
                    )
                )
    return findings


def check_envelope(data: Any, expected_type: str, stage: str, path: str) -> list[Finding]:
    if not isinstance(data, dict):
        return [finding("ENV-E001", "error", "structural", stage, path, "contract must be a JSON object")]
    findings: list[Finding] = []
    if data.get("schema_version") != "0.2.0":
        findings.append(
            finding(
                "ENV-E002",
                "error",
                "structural",
                stage,
                path,
                "schema_version must be 0.2.0",
                pointer="/schema_version",
            )
        )
    if data.get("artifact_type") != expected_type:
        findings.append(
            finding(
                "ENV-E003",
                "error",
                "structural",
                stage,
                path,
                f"artifact_type must be {expected_type}",
                pointer="/artifact_type",
            )
        )
    if not nonempty(data.get("project_id")):
        findings.append(finding("ENV-E004", "error", "structural", stage, path, "project_id is required"))
    review = data.get("review")
    if not isinstance(review, dict) or review.get("decision") not in REVIEW_DECISIONS:
        findings.append(
            finding(
                "ENV-E005",
                "error",
                "semantic",
                stage,
                path,
                "review.decision must use the v0.2 review vocabulary",
                pointer="/review/decision",
            )
        )
    return findings


def check_state(data: Any, path: str) -> list[Finding]:
    findings = check_envelope(data, "workflow_state", "intake", path)
    if not isinstance(data, dict):
        return findings
    if data.get("workflow_version") != "0.2.0":
        findings.append(finding("STATE-E001", "error", "structural", "intake", path, "workflow_version must be 0.2.0"))
    current = data.get("current_stage")
    stages = data.get("stages")
    if current not in STAGES:
        findings.append(finding("STATE-E002", "error", "structural", "intake", path, "current_stage is invalid"))
    if not isinstance(stages, dict):
        findings.append(finding("STATE-E003", "error", "structural", "intake", path, "stages must be an object"))
        return findings
    for stage in STAGES:
        if stage not in stages:
            findings.append(finding("STATE-E004", "error", "structural", "intake", path, f"missing stage: {stage}"))
        elif stages[stage] not in STAGE_STATUSES:
            findings.append(finding("STATE-E005", "error", "structural", "intake", path, f"invalid status for {stage}"))
    extra = sorted(set(stages) - set(STAGES))
    if extra:
        findings.append(finding("STATE-E006", "error", "structural", "intake", path, f"unknown stages: {', '.join(extra)}"))
    if current in STAGES:
        index = STAGES.index(current)
        for prior in STAGES[:index]:
            if stages.get(prior) != "passed":
                findings.append(
                    finding("STATE-E007", "error", "structural", prior, path, f"prior stage must pass before {current}: {prior}")
                )
        for later in STAGES[index + 1 :]:
            if stages.get(later) in {"in_progress", "awaiting_review", "passed"}:
                findings.append(
                    finding("STATE-E008", "error", "structural", later, path, f"later stage active before {current} passes: {later}")
                )
    return findings


def check_sources(data: Any, root: Path, path: str) -> list[Finding]:
    findings = check_envelope(data, "source_manifest", "intake", path)
    if not isinstance(data, dict):
        return findings
    sources = data.get("sources")
    findings.extend(require_fields(sources, ("path", "sha256", "origin"), ("source_id",), "SOURCE", "intake", path))
    for index, source in enumerate(as_list(sources)):
        if not isinstance(source, dict):
            continue
        ident = item_id(source, "source_id")
        rel = source.get("path")
        file_path = safe_project_path(root, rel)
        if file_path is None:
            findings.append(finding("SOURCE-E006", "error", "structural", "intake", path, f"unsafe source path: {rel}", related_ids=[ident]))
            continue
        if not file_path.is_file():
            findings.append(finding("SOURCE-E007", "error", "structural", "intake", path, f"missing source file: {rel}", related_ids=[ident]))
            continue
        if source.get("sha256") != sha256(file_path):
            findings.append(finding("SOURCE-E008", "error", "structural", "intake", path, f"source hash mismatch: {rel}", related_ids=[ident]))
        if source.get("size") is not None and source.get("size") != file_path.stat().st_size:
            findings.append(finding("SOURCE-E009", "error", "structural", "intake", path, f"source size mismatch: {rel}", related_ids=[ident]))
        if source.get("mutable") is not False and source.get("origin") in {"official", "organizer_attachment"}:
            findings.append(finding("SOURCE-E010", "error", "semantic", "intake", path, f"official source must declare mutable=false: {ident}"))
    return findings


def check_facts(data: Any, source_ids: set[str], path: str) -> list[Finding]:
    findings = check_envelope(data, "problem_facts", "problem-analysis", path)
    if not isinstance(data, dict):
        return findings
    subproblems = data.get("subproblems")
    facts = data.get("facts")
    findings.extend(require_fields(subproblems, ("request", "expected_output"), ("subproblem_id", "id"), "SUBPROBLEM", "problem-analysis", path))
    findings.extend(require_fields(facts, ("statement", "source_id", "location"), ("fact_id", "id"), "FACT", "problem-analysis", path))
    for fact in as_list(facts):
        if not isinstance(fact, dict):
            continue
        ident = item_id(fact, "fact_id", "id")
        source_id = fact.get("source_id")
        if source_id not in source_ids:
            findings.append(finding("FACT-E006", "error", "structural", "problem-analysis", path, f"{ident} cites unknown source: {source_id}", related_ids=[ident, str(source_id)]))
        if fact.get("extraction_method") == "ocr" and fact.get("render_verified") is not True:
            findings.append(finding("FACT-E007", "error", "visual", "problem-analysis", path, f"OCR-routed fact lacks rendered-page verification: {ident}", related_ids=[ident]))
    return findings


def check_capabilities(data: Any, root: Path, fact_ids: set[str], subproblem_ids: set[str], path: str) -> list[Finding]:
    findings = check_envelope(data, "task_capabilities", "problem-analysis", path)
    if not isinstance(data, dict):
        return findings
    capabilities = data.get("capabilities")
    findings.extend(
        require_fields(
            capabilities,
            ("subproblem_id", "objective", "required_output", "acceptance_checks"),
            ("capability_id",),
            "CAP",
            "problem-analysis",
            path,
        )
    )
    owned_subproblems: set[str] = set()
    for capability in as_list(capabilities):
        if not isinstance(capability, dict):
            continue
        ident = item_id(capability, "capability_id")
        subproblem = capability.get("subproblem_id")
        if subproblem not in subproblem_ids:
            findings.append(finding("CAP-E006", "error", "structural", "problem-analysis", path, f"{ident} names unknown subproblem: {subproblem}", related_ids=[ident]))
        else:
            owned_subproblems.add(str(subproblem))
        for fact_id in as_list(capability.get("fact_ids")):
            if fact_id not in fact_ids:
                findings.append(finding("CAP-E007", "error", "structural", "problem-analysis", path, f"{ident} names unknown fact: {fact_id}", related_ids=[ident, str(fact_id)]))
        checks = capability.get("acceptance_checks")
        if not isinstance(checks, list) or not checks:
            findings.append(finding("CAP-E008", "error", "semantic", "problem-analysis", path, f"{ident} has no observable acceptance check", related_ids=[ident]))
        if capability.get("lifecycle_state") in {"implemented", "executed", "validated"}:
            entry_points = as_list(capability.get("code_entry_points"))
            if not entry_points:
                findings.append(finding("CAP-E010", "error", "execution", "computation", path, f"implemented capability has no code entry point: {ident}", related_ids=[ident]))
            for entry_point in entry_points:
                rel = str(entry_point).split(":", 1)[0]
                code_path = safe_project_path(root, rel)
                if code_path is None or not code_path.is_file():
                    findings.append(finding("CAP-E011", "error", "execution", "computation", path, f"capability code entry point is missing: {entry_point}", related_ids=[ident]))
    missing = sorted(subproblem_ids - owned_subproblems)
    if missing:
        findings.append(finding("CAP-E009", "error", "semantic", "problem-analysis", path, f"subproblems without capability ownership: {', '.join(missing)}", related_ids=missing))
    return findings


def check_model(data: Any, capability_ids: set[str], path: str, profile: str) -> list[Finding]:
    findings = check_envelope(data, "model_contract", "model-design", path)
    if not isinstance(data, dict):
        return findings
    components = data.get("components")
    findings.extend(
        require_fields(
            components,
            ("capability_ids", "variables", "inputs", "outputs", "method", "scope", "verification_plan"),
            ("model_id",),
            "MODEL",
            "model-design",
            path,
        )
    )
    owned: set[str] = set()
    for component in as_list(components):
        if not isinstance(component, dict):
            continue
        ident = item_id(component, "model_id")
        for capability_id in as_list(component.get("capability_ids")):
            if capability_id not in capability_ids:
                findings.append(finding("MODEL-E006", "error", "structural", "model-design", path, f"{ident} owns unknown capability: {capability_id}", related_ids=[ident, str(capability_id)]))
            else:
                owned.add(capability_id)
        if profile == "strict" and not as_list(component.get("alternatives_considered")):
            findings.append(finding("MODEL-E007", "warning", "semantic", "model-design", path, f"strict profile has no recorded alternative for {ident}", related_ids=[ident]))
    missing = sorted(capability_ids - owned)
    if missing:
        findings.append(finding("MODEL-E008", "error", "semantic", "model-design", path, f"capabilities without model ownership: {', '.join(missing)}", related_ids=missing))
    return findings


def check_cross_question(data: Any, subproblem_ids: set[str], path: str) -> list[Finding]:
    findings = check_envelope(data, "cross_question_ledger", "model-design", path)
    if not isinstance(data, dict):
        return findings
    items = data.get("shared_items")
    findings.extend(require_fields(items, ("name", "producer", "consumers", "definition", "unit"), ("shared_id",), "CROSS", "model-design", path))
    signatures: dict[str, tuple[Any, Any]] = {}
    for item in as_list(items):
        if not isinstance(item, dict):
            continue
        ident = item_id(item, "shared_id")
        for subproblem in [item.get("producer"), *as_list(item.get("consumers"))]:
            if subproblem not in subproblem_ids and subproblem != "official_source":
                findings.append(finding("CROSS-E006", "error", "structural", "model-design", path, f"{ident} names unknown subproblem: {subproblem}", related_ids=[ident]))
        name = str(item.get("name", "")).strip().casefold()
        signature = (item.get("definition"), item.get("unit"))
        if name in signatures and signatures[name] != signature:
            findings.append(finding("CROSS-E007", "error", "semantic", "model-design", path, f"shared name has incompatible definition or unit: {item.get('name')}", related_ids=[ident]))
        signatures[name] = signature
    return findings


def discover_run_manifests(root: Path) -> list[Path]:
    runs = root / "runs"
    return sorted(runs.glob("*/RUN_MANIFEST.json")) if runs.is_dir() else []


def check_run(data: Any, root: Path, rel_path: str, capability_ids: set[str]) -> list[Finding]:
    findings = check_envelope(data, "run_manifest", "computation", rel_path)
    if not isinstance(data, dict):
        return findings
    required = ("run_id", "purpose", "capability_ids", "argv", "working_directory", "started_at", "finished_at", "exit_code", "status", "inputs", "outputs", "environment", "stdout_path", "stderr_path")
    for field_name in required:
        if data.get(field_name) in (None, "", []):
            findings.append(finding("RUN-E001", "error", "execution", "computation", rel_path, f"missing run field: {field_name}", pointer=f"/{field_name}"))
    if data.get("status") != "completed" or data.get("exit_code") != 0:
        findings.append(finding("RUN-E002", "error", "execution", "computation", rel_path, "run must record completed status and exit code 0"))
    for capability_id in as_list(data.get("capability_ids")):
        if capability_id not in capability_ids:
            findings.append(finding("RUN-E003", "error", "structural", "computation", rel_path, f"run names unknown capability: {capability_id}", related_ids=[str(capability_id)]))
    for kind in ("inputs", "outputs"):
        values = data.get(kind)
        if not isinstance(values, list) or (kind == "outputs" and not values):
            findings.append(finding("RUN-E004", "error", "execution", "computation", rel_path, f"{kind} must be a {'nonempty ' if kind == 'outputs' else ''}list"))
            continue
        for index, entry in enumerate(values):
            if not isinstance(entry, dict):
                findings.append(finding("RUN-E005", "error", "structural", "computation", rel_path, f"{kind} entry must be an object"))
                continue
            file_path = safe_project_path(root, entry.get("path"))
            if file_path is None or not file_path.is_file() or file_path.stat().st_size == 0:
                findings.append(finding("RUN-E006", "error", "execution", "computation", rel_path, f"missing or empty {kind[:-1]}: {entry.get('path')}"))
                continue
            if entry.get("sha256") != sha256(file_path):
                findings.append(finding("RUN-E007", "error", "execution", "computation", rel_path, f"hash mismatch for {kind[:-1]}: {entry.get('path')}"))
            if entry.get("size") != file_path.stat().st_size:
                findings.append(finding("RUN-E013", "error", "execution", "computation", rel_path, f"size mismatch for {kind[:-1]}: {entry.get('path')}"))
    for log_name in ("stdout_path", "stderr_path"):
        log_path = safe_project_path(root, data.get(log_name))
        if log_path is None or not log_path.is_file():
            findings.append(finding("RUN-E012", "error", "execution", "computation", rel_path, f"missing recorded log: {data.get(log_name)}"))
    assertions = data.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        findings.append(finding("RUN-W001", "warning", "numerical", "computation", rel_path, "run records no assertions"))
    elif any(isinstance(item, dict) and item.get("passed") is not True for item in assertions):
        findings.append(finding("RUN-E008", "error", "numerical", "computation", rel_path, "one or more recorded assertions failed"))
    return findings


def resolve_json_pointer(data: Any, pointer: str) -> tuple[Any, bool]:
    if pointer in {"", "/"}:
        return data, True
    current = data
    for raw in pointer.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, dict) and token in current:
            current = current[token]
        elif isinstance(current, list) and token.isdigit() and int(token) < len(current):
            current = current[int(token)]
        else:
            return None, False
    return current, True


def check_results(data: Any, root: Path, run_ids: set[str], path: str) -> list[Finding]:
    findings = check_envelope(data, "results_index", "computation", path)
    if not isinstance(data, dict):
        return findings
    results = data.get("results")
    findings.extend(require_fields(results, ("name", "unit", "run_id", "output_locator", "scope", "evidence_state"), ("result_id",), "RESULT", "computation", path))
    for result in as_list(results):
        if not isinstance(result, dict):
            continue
        ident = item_id(result, "result_id")
        if result.get("run_id") not in run_ids:
            findings.append(finding("RESULT-E006", "error", "execution", "computation", path, f"{ident} names unknown run: {result.get('run_id')}", related_ids=[ident]))
        if result.get("evidence_state") not in EVIDENCE_STATES:
            findings.append(finding("RESULT-E007", "error", "structural", "computation", path, f"{ident} has invalid evidence_state", related_ids=[ident]))
        locator = result.get("output_locator")
        if not nonempty(locator) or "#" not in locator:
            findings.append(finding("RESULT-E008", "error", "execution", "computation", path, f"{ident} output_locator must be path#JSON-pointer", related_ids=[ident]))
            continue
        rel, pointer = locator.split("#", 1)
        output_path = safe_project_path(root, rel)
        if output_path is None or not output_path.is_file():
            findings.append(finding("RESULT-E009", "error", "execution", "computation", path, f"{ident} output file is missing: {rel}", related_ids=[ident]))
            continue
        output_data, error = read_json(output_path)
        if error:
            findings.append(finding("RESULT-E010", "error", "execution", "computation", path, f"{ident} output is not readable JSON: {error}", related_ids=[ident]))
            continue
        stored_value, found = resolve_json_pointer(output_data, pointer)
        if not found:
            findings.append(finding("RESULT-E011", "error", "execution", "computation", path, f"{ident} JSON pointer does not resolve: {pointer}", related_ids=[ident]))
        elif "value" in result and result.get("value") != stored_value:
            findings.append(finding("RESULT-E012", "error", "numerical", "computation", path, f"{ident} indexed value differs from executed output", related_ids=[ident]))
    return findings


def claim_certificate_types(text: str) -> set[str]:
    return {name for name, pattern in STRONG_CLAIM_PATTERNS.items() if pattern.search(text)}


def check_claims(
    data: Any,
    known_ids: dict[str, set[str]],
    path: str,
    profile: str,
) -> list[Finding]:
    findings = check_envelope(data, "claim_ledger", "validation", path)
    if not isinstance(data, dict):
        return findings
    claims = data.get("claims")
    findings.extend(require_fields(claims, ("text", "claim_type", "scope", "evidence_state"), ("claim_id",), "CLAIM", "validation", path))
    review = data.get("independent_review")
    if not isinstance(review, dict) or review.get("decision") not in {"accepted", "revision_requested"}:
        findings.append(finding("CLAIM-E006", "error", "semantic", "validation", path, f"{profile} profile requires a recorded independent logic pass"))
    for claim in as_list(claims):
        if not isinstance(claim, dict):
            continue
        ident = item_id(claim, "claim_id")
        text = str(claim.get("text", ""))
        state = claim.get("evidence_state")
        if state not in EVIDENCE_STATES:
            findings.append(finding("CLAIM-E007", "error", "structural", "validation", path, f"{ident} has invalid evidence_state", related_ids=[ident]))
        refs = claim.get("evidence", {})
        if not isinstance(refs, dict):
            findings.append(finding("CLAIM-E008", "error", "structural", "validation", path, f"{ident} evidence must be an object", related_ids=[ident]))
            refs = {}
        mapping = {
            "fact_ids": "facts",
            "model_ids": "models",
            "run_ids": "runs",
            "result_ids": "results",
            "figure_ids": "figures",
        }
        referenced = 0
        for field_name, known_name in mapping.items():
            for ref in as_list(refs.get(field_name)):
                referenced += 1
                if ref not in known_ids.get(known_name, set()):
                    findings.append(finding("CLAIM-E009", "error", "structural", "validation", path, f"{ident} names unknown {known_name[:-1]}: {ref}", related_ids=[ident, str(ref)]))
        if state in {"supported_not_reproduced", "reproduced", "partially_supported"} and referenced == 0:
            findings.append(finding("CLAIM-E010", "error", "semantic", "validation", path, f"{ident} requires linked evidence", related_ids=[ident]))
        certificate_types = claim_certificate_types(text)
        certificates = as_list(claim.get("certificates"))
        declared_types = {item.get("type") for item in certificates if isinstance(item, dict)}
        missing = sorted(certificate_types - declared_types)
        if missing and state in {"supported_not_reproduced", "reproduced", "partially_supported"}:
            findings.append(finding("CLAIM-E011", "error", "semantic", "validation", path, f"strong claim lacks certificate declaration: {', '.join(missing)}", related_ids=[ident]))
        all_known_evidence = set().union(*known_ids.values()) if known_ids else set()
        for certificate in certificates:
            if not isinstance(certificate, dict) or not nonempty(certificate.get("type")):
                findings.append(finding("CLAIM-E015", "error", "structural", "validation", path, f"{ident} has malformed certificate", related_ids=[ident]))
                continue
            evidence_ids = as_list(certificate.get("evidence_ids"))
            if not nonempty(certificate.get("description")) or not evidence_ids:
                findings.append(finding("CLAIM-E016", "error", "semantic", "validation", path, f"{ident} certificate lacks description or evidence IDs: {certificate.get('type')}", related_ids=[ident]))
            for evidence_id in evidence_ids:
                if evidence_id not in all_known_evidence:
                    findings.append(finding("CLAIM-E017", "error", "structural", "validation", path, f"{ident} certificate names unknown evidence: {evidence_id}", related_ids=[ident, str(evidence_id)]))
            if certificate.get("type") == "global_optimality" and not nonempty(certificate.get("scope")):
                findings.append(finding("CLAIM-E018", "error", "semantic", "validation", path, f"{ident} global-optimality certificate lacks feasible-set scope", related_ids=[ident]))
            if certificate.get("type") == "robustness" and certificate.get("method") not in {"perturbation", "sensitivity", "out_of_sample", "stress_test"}:
                findings.append(finding("CLAIM-E019", "error", "semantic", "validation", path, f"{ident} robustness certificate lacks a recognized validation method", related_ids=[ident]))
        if state == "reproduced" and not as_list(refs.get("run_ids")):
            findings.append(finding("CLAIM-E012", "error", "execution", "validation", path, f"reproduced claim has no run evidence: {ident}", related_ids=[ident]))
        if state == "reproduced" and not isinstance(claim.get("reproduction"), dict):
            findings.append(finding("CLAIM-E013", "error", "execution", "validation", path, f"reproduced claim lacks claim-specific rerun comparison: {ident}", related_ids=[ident]))
        if state in {"supported_not_reproduced", "reproduced", "partially_supported"}:
            review = claim.get("review")
            if not isinstance(review, dict) or review.get("decision") != "accepted":
                findings.append(finding("CLAIM-E014", "error", "semantic", "validation", path, f"supported claim lacks accepted review: {ident}", related_ids=[ident]))
    return findings


def check_figures(data: Any, root: Path, result_ids: set[str], run_ids: set[str], path: str, profile: str) -> list[Finding]:
    findings = check_envelope(data, "figure_manifest", "paper", path)
    if not isinstance(data, dict):
        return findings
    figures = data.get("figures")
    findings.extend(require_fields(figures, ("kind", "purpose", "path", "sha256", "caption_claims", "visual_review"), ("figure_id",), "FIGURE", "paper", path))
    for figure in as_list(figures):
        if not isinstance(figure, dict):
            continue
        ident = item_id(figure, "figure_id")
        kind = figure.get("kind")
        figure_path = safe_project_path(root, figure.get("path"))
        if figure_path is None or not figure_path.is_file() or figure_path.stat().st_size == 0:
            findings.append(finding("FIGURE-E010", "error", "visual", "paper", path, f"missing or empty figure file: {figure.get('path')}", related_ids=[ident]))
        elif figure.get("sha256") != sha256(figure_path):
            findings.append(finding("FIGURE-E011", "error", "structural", "paper", path, f"figure hash mismatch: {figure.get('path')}", related_ids=[ident]))
        for result_id in as_list(figure.get("result_ids")):
            if result_id not in result_ids:
                findings.append(finding("FIGURE-E006", "error", "structural", "paper", path, f"{ident} names unknown result: {result_id}", related_ids=[ident, str(result_id)]))
        for run_id in as_list(figure.get("run_ids")):
            if run_id not in run_ids:
                findings.append(finding("FIGURE-E007", "error", "structural", "paper", path, f"{ident} names unknown run: {run_id}", related_ids=[ident, str(run_id)]))
        if kind != "conceptual" and not as_list(figure.get("result_ids")):
            findings.append(finding("FIGURE-E008", "error", "semantic", "paper", path, f"quantitative figure lacks result provenance: {ident}", related_ids=[ident]))
        review = figure.get("visual_review")
        if not isinstance(review, dict) or review.get("decision") != "accepted":
            severity = "error" if profile == "strict" else "warning"
            findings.append(finding("FIGURE-E009", severity, "visual", "paper", path, f"figure lacks accepted visual review: {ident}", related_ids=[ident]))
    return findings


def check_delivery(data: Any, root: Path, path: str, profile: str) -> list[Finding]:
    findings = check_envelope(data, "delivery_manifest", "delivery", path)
    if not isinstance(data, dict):
        return findings
    if data.get("profile") != profile:
        findings.append(finding("DELIVERY-E001", "error", "structural", "delivery", path, "delivery profile does not match requested profile"))
    files = data.get("files")
    findings.extend(require_fields(files, ("path", "role", "sha256", "size"), ("path",), "DELIVERY", "delivery", path))
    for item in as_list(files):
        if not isinstance(item, dict):
            continue
        rel = item.get("path")
        file_path = safe_project_path(root, rel)
        if file_path is None or not file_path.is_file() or file_path.stat().st_size == 0:
            findings.append(finding("DELIVERY-E006", "error", "structural", "delivery", path, f"missing or empty delivery file: {rel}"))
            continue
        if item.get("sha256") != sha256(file_path):
            findings.append(finding("DELIVERY-E007", "error", "structural", "delivery", path, f"delivery hash mismatch: {rel}"))
        if item.get("size") != file_path.stat().st_size:
            findings.append(finding("DELIVERY-E008", "error", "structural", "delivery", path, f"delivery size mismatch: {rel}"))
    compile_record = data.get("compile")
    if not isinstance(compile_record, dict) or compile_record.get("exit_code") != 0 or not compile_record.get("command"):
        findings.append(finding("DELIVERY-E009", "error", "execution", "delivery", path, "successful compile record is required"))
    elif safe_project_path(root, compile_record.get("log_path")) is None or not safe_project_path(root, compile_record.get("log_path")).is_file():
        findings.append(finding("DELIVERY-E012", "error", "execution", "delivery", path, "compile log is missing"))
    unresolved = as_list(data.get("unresolved_errors"))
    if unresolved:
        findings.append(finding("DELIVERY-E010", "error", "semantic", "delivery", path, "delivery contains unresolved errors"))
    final_review = data.get("final_review")
    if not isinstance(final_review, dict) or final_review.get("decision") != "accepted":
        findings.append(finding("DELIVERY-E011", "error", "semantic", "delivery", path, "final human review must be accepted"))
    return findings


def load_contracts(root: Path, required: Iterable[str]) -> tuple[dict[str, Any], list[Finding]]:
    data: dict[str, Any] = {}
    findings: list[Finding] = []
    for name in required:
        rel = CONTRACT_PATHS[name]
        path = root / rel
        if not path.is_file():
            findings.append(
                finding(
                    "PROJECT-E001",
                    "error",
                    "structural",
                    owning_stage_for_contract(name),
                    rel,
                    f"required contract is missing: {rel}",
                )
            )
            continue
        value, error = read_json(path)
        if error:
            findings.append(
                finding(
                    "PROJECT-E002",
                    "error",
                    "structural",
                    owning_stage_for_contract(name),
                    rel,
                    f"invalid JSON: {error}",
                )
            )
            continue
        data[name] = value
    return data, findings


def owning_stage_for_contract(name: str) -> str:
    return {
        "state": "intake",
        "sources": "intake",
        "facts": "problem-analysis",
        "capabilities": "problem-analysis",
        "model": "model-design",
        "cross_question": "model-design",
        "results": "computation",
        "claims": "validation",
        "figures": "paper",
        "delivery": "delivery",
    }[name]


def check_project(root: Path, stage: str, profile: str) -> tuple[list[Finding], dict[str, Any]]:
    if stage not in STAGES:
        raise ValueError(f"unknown stage: {stage}")
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    required = STAGE_CONTRACTS[stage]
    contracts, findings = load_contracts(root, required)
    if stage == "validation" and "figures" not in contracts:
        optional_figure_path = root / CONTRACT_PATHS["figures"]
        if optional_figure_path.is_file():
            optional_figures, error = read_json(optional_figure_path)
            if error:
                findings.append(
                    finding(
                        "PROJECT-E002",
                        "error",
                        "structural",
                        "paper",
                        CONTRACT_PATHS["figures"],
                        f"invalid optional figure manifest: {error}",
                    )
                )
            else:
                contracts["figures"] = optional_figures

    project_ids = {
        value.get("project_id")
        for value in contracts.values()
        if isinstance(value, dict) and nonempty(value.get("project_id"))
    }
    if len(project_ids) > 1:
        findings.append(
            finding(
                "PROJECT-E003",
                "error",
                "structural",
                "intake",
                ".",
                f"contracts contain mixed project IDs: {', '.join(sorted(project_ids))}",
            )
        )

    source_ids: set[str] = set()
    fact_ids: set[str] = set()
    subproblem_ids: set[str] = set()
    capability_ids: set[str] = set()
    model_ids: set[str] = set()
    result_ids: set[str] = set()
    figure_ids: set[str] = set()

    if "state" in contracts:
        findings.extend(check_schema(contracts["state"], "state", "intake", CONTRACT_PATHS["state"]))
        findings.extend(check_state(contracts["state"], CONTRACT_PATHS["state"]))
    if "sources" in contracts:
        findings.extend(check_schema(contracts["sources"], "sources", "intake", CONTRACT_PATHS["sources"]))
        findings.extend(check_sources(contracts["sources"], root, CONTRACT_PATHS["sources"]))
        source_ids = ids(contracts["sources"].get("sources"), "source_id") if isinstance(contracts["sources"], dict) else set()
    if "facts" in contracts:
        findings.extend(check_schema(contracts["facts"], "facts", "problem-analysis", CONTRACT_PATHS["facts"]))
        findings.extend(check_facts(contracts["facts"], source_ids, CONTRACT_PATHS["facts"]))
        if isinstance(contracts["facts"], dict):
            fact_ids = ids(contracts["facts"].get("facts"), "fact_id", "id")
            subproblem_ids = ids(contracts["facts"].get("subproblems"), "subproblem_id", "id")
    if "capabilities" in contracts:
        findings.extend(check_schema(contracts["capabilities"], "capabilities", "problem-analysis", CONTRACT_PATHS["capabilities"]))
        findings.extend(check_capabilities(contracts["capabilities"], root, fact_ids, subproblem_ids, CONTRACT_PATHS["capabilities"]))
        capability_ids = ids(contracts["capabilities"].get("capabilities"), "capability_id") if isinstance(contracts["capabilities"], dict) else set()
    if "model" in contracts:
        findings.extend(check_schema(contracts["model"], "model", "model-design", CONTRACT_PATHS["model"]))
        findings.extend(check_model(contracts["model"], capability_ids, CONTRACT_PATHS["model"], profile))
        model_ids = ids(contracts["model"].get("components"), "model_id") if isinstance(contracts["model"], dict) else set()
    if "cross_question" in contracts:
        findings.extend(check_schema(contracts["cross_question"], "cross_question", "model-design", CONTRACT_PATHS["cross_question"]))
        findings.extend(check_cross_question(contracts["cross_question"], subproblem_ids, CONTRACT_PATHS["cross_question"]))

    run_ids: set[str] = set()
    executed_capability_ids: set[str] = set()
    run_count = 0
    if STAGES.index(stage) >= STAGES.index("computation"):
        run_paths = discover_run_manifests(root)
        if not run_paths:
            findings.append(finding("RUN-E009", "error", "execution", "computation", "runs/", "no run manifests found"))
        for run_path in run_paths:
            rel = run_path.relative_to(root).as_posix()
            run, error = read_json(run_path)
            if error:
                findings.append(finding("RUN-E010", "error", "structural", "computation", rel, f"invalid run JSON: {error}"))
                continue
            run_count += 1
            findings.extend(check_schema(run, "run", "computation", rel))
            if isinstance(run, dict) and nonempty(run.get("run_id")):
                if run["run_id"] in run_ids:
                    findings.append(finding("RUN-E011", "error", "structural", "computation", rel, f"duplicate run ID: {run['run_id']}"))
                run_ids.add(run["run_id"])
                executed_capability_ids.update(str(value) for value in as_list(run.get("capability_ids")))
            findings.extend(check_run(run, root, rel, capability_ids))
        if "capabilities" in contracts and isinstance(contracts["capabilities"], dict):
            for capability in as_list(contracts["capabilities"].get("capabilities")):
                if not isinstance(capability, dict) or capability.get("lifecycle_state") not in {"executed", "validated"}:
                    continue
                capability_id = item_id(capability, "capability_id")
                if capability_id not in executed_capability_ids:
                    findings.append(
                        finding(
                            "RUN-E014",
                            "error",
                            "execution",
                            "computation",
                            CONTRACT_PATHS["capabilities"],
                            f"capability declares execution without a run: {capability_id}",
                            related_ids=[capability_id],
                        )
                    )
    if "results" in contracts:
        findings.extend(check_schema(contracts["results"], "results", "computation", CONTRACT_PATHS["results"]))
        findings.extend(check_results(contracts["results"], root, run_ids, CONTRACT_PATHS["results"]))
        result_ids = ids(contracts["results"].get("results"), "result_id") if isinstance(contracts["results"], dict) else set()
        if "capabilities" in contracts and isinstance(contracts["capabilities"], dict):
            for capability in as_list(contracts["capabilities"].get("capabilities")):
                if not isinstance(capability, dict):
                    continue
                capability_id = item_id(capability, "capability_id")
                for result_id in as_list(capability.get("result_ids")):
                    if result_id not in result_ids:
                        findings.append(finding("RESULT-E013", "error", "structural", "computation", CONTRACT_PATHS["capabilities"], f"{capability_id} expects unknown result: {result_id}", related_ids=[capability_id, str(result_id)]))
    if "figures" in contracts:
        findings.extend(check_schema(contracts["figures"], "figures", "paper", CONTRACT_PATHS["figures"]))
        if isinstance(contracts["figures"], dict):
            figure_ids = ids(contracts["figures"].get("figures"), "figure_id")
        findings.extend(check_figures(contracts["figures"], root, result_ids, run_ids, CONTRACT_PATHS["figures"], profile))
    if "claims" in contracts:
        findings.extend(check_schema(contracts["claims"], "claims", "validation", CONTRACT_PATHS["claims"]))
        known = {
            "facts": fact_ids,
            "models": model_ids,
            "runs": run_ids,
            "results": result_ids,
            "figures": figure_ids,
        }
        findings.extend(check_claims(contracts["claims"], known, CONTRACT_PATHS["claims"], profile))
    if "delivery" in contracts:
        findings.extend(check_schema(contracts["delivery"], "delivery", "delivery", CONTRACT_PATHS["delivery"]))
        findings.extend(check_delivery(contracts["delivery"], root, CONTRACT_PATHS["delivery"], profile))

    state = contracts.get("state")
    state_map = state.get("stages", {}) if isinstance(state, dict) else {}
    for name, contract in contracts.items():
        if name == "state" or not isinstance(contract, dict):
            continue
        owner = owning_stage_for_contract(name)
        if state_map.get(owner) == "passed":
            review = contract.get("review")
            if not isinstance(review, dict) or review.get("decision") != "accepted":
                findings.append(
                    finding(
                        "REVIEW-E001",
                        "error",
                        "semantic",
                        owner,
                        CONTRACT_PATHS[name],
                        f"passed stage owns an unaccepted contract: {name}",
                    )
                )

    summary = {
        "project_ids": sorted(project_ids),
        "stage": stage,
        "profile": profile,
        "contracts_loaded": sorted(contracts),
        "run_count": run_count,
        "finding_counts": {
            level: sum(item.severity == level for item in findings)
            for level in ("error", "warning", "info")
        },
        "evidence_boundary": (
            "Passing establishes declared structure, traceability, preserved execution, "
            "and recorded reviews only; it does not prove mathematical correctness."
        ),
    }
    return findings, summary
