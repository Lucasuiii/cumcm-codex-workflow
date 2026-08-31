#!/usr/bin/env python3
"""Deterministic v0.4 contract and cross-artifact checks.

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
GATE_MODES = {"preflight", "enforce"}
WORKFLOW_VERSION = "0.4.0"
PAPER_LAYER_NAMES = {
    "problem_interpretation",
    "assumptions_boundaries",
    "variables_parameters",
    "objective_constraints",
    "derivation",
    "algorithm",
    "results",
    "validation",
    "limitations",
}

CONTRACT_PATHS = {
    "state": ".cumcm/state.json",
    "sources": "problem/SOURCE_MANIFEST.json",
    "facts": "analysis/PROBLEM_FACTS.json",
    "capabilities": "analysis/TASK_CAPABILITIES.json",
    "model": "model/MODEL_CONTRACT.json",
    "cross_question": "model/CROSS_QUESTION_LEDGER.json",
    "results": "results/RESULTS_INDEX.json",
    "independent_review_package": "validation/independent-review-package/REVIEW_PACKAGE_MANIFEST.json",
    "independent_review_result": "validation/INDEPENDENT_REVIEW_RESULT.json",
    "claims": "validation/CLAIM_LEDGER.json",
    "figures": "figures/FIGURE_MANIFEST.json",
    "paper_plan": "paper/PAPER_PLAN.json",
    "latex_template": "paper/LATEX_TEMPLATE_MANIFEST.json",
    "paper_quality": "paper/PAPER_QUALITY_REPORT.json",
    "paper_revisions": "paper/PAPER_REVISION_LOG.json",
    "paper_traceability": "paper/PAPER_TRACEABILITY.json",
    "paper_visible_text": "paper/PAPER_VISIBLE_TEXT_REPORT.json",
    "delivery": "delivery/DELIVERY_MANIFEST.json",
    "compile_receipt": "delivery/COMPILE_RECEIPT.json",
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
    "validation": ("state", "sources", "facts", "capabilities", "model", "cross_question", "results", "independent_review_package", "independent_review_result", "claims"),
    "paper": ("state", "sources", "facts", "capabilities", "model", "cross_question", "results", "independent_review_package", "independent_review_result", "claims", "figures", "paper_plan", "latex_template", "paper_quality", "paper_revisions", "paper_traceability", "paper_visible_text"),
    "delivery": ("state", "sources", "facts", "capabilities", "model", "cross_question", "results", "independent_review_package", "independent_review_result", "claims", "figures", "paper_plan", "latex_template", "paper_quality", "paper_revisions", "paper_traceability", "paper_visible_text", "delivery", "compile_receipt"),
}

PAPER_CONTRACTS = ("paper_plan", "latex_template", "paper_quality", "paper_revisions", "paper_traceability", "paper_visible_text")

SCHEMA_FILES = {
    "state": "workflow-state.schema.json",
    "sources": "source-manifest.schema.json",
    "facts": "problem-facts.schema.json",
    "capabilities": "task-capabilities.schema.json",
    "model": "model-contract.schema.json",
    "cross_question": "cross-question-ledger.schema.json",
    "results": "results-index.schema.json",
    "independent_review_package": "independent-review-package.schema.json",
    "independent_review_result": "independent-review-result.schema.json",
    "claims": "claim-ledger.schema.json",
    "figures": "figure-manifest.schema.json",
    "paper_plan": "paper-plan.schema.json",
    "latex_template": "latex-template-manifest.schema.json",
    "paper_quality": "paper-quality-report.schema.json",
    "paper_revisions": "paper-revision-log.schema.json",
    "paper_traceability": "paper-traceability.schema.json",
    "paper_visible_text": "paper-visible-text-report.schema.json",
    "delivery": "delivery-manifest.schema.json",
    "compile_receipt": "compile-receipt.schema.json",
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
    gate_only: bool = False

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
    gate_only: bool = False,
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
        gate_only=gate_only,
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
    if data.get("schema_version") != WORKFLOW_VERSION:
        findings.append(
            finding(
                "ENV-E002",
                "error",
                "structural",
                stage,
                path,
                "schema_version must be 0.4.0",
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
                "review.decision must use the workflow review vocabulary",
                pointer="/review/decision",
            )
        )
    return findings


def check_state(data: Any, path: str) -> list[Finding]:
    findings = check_envelope(data, "workflow_state", "intake", path)
    if not isinstance(data, dict):
        return findings
    if data.get("workflow_version") != WORKFLOW_VERSION:
        findings.append(finding("STATE-E001", "error", "structural", "intake", path, "workflow_version must be 0.4.0"))
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
    findings.extend(require_fields(sources, ("path", "origin", "acquisition"), ("source_id",), "SOURCE", "intake", path))
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
        recorded_hash = source.get("sha256")
        if source.get("origin") in {"official", "organizer_attachment"}:
            if not nonempty(recorded_hash) or recorded_hash != sha256(file_path):
                findings.append(finding("SOURCE-E008", "error", "structural", "intake", path, f"official source hash is missing or mismatched: {rel}", related_ids=[ident]))
        elif nonempty(recorded_hash) and recorded_hash != sha256(file_path):
            findings.append(finding("SOURCE-W008", "warning", "structural", "intake", path, f"optional source hash is stale: {rel}", related_ids=[ident]))
        if source.get("size") is not None and source.get("size") != file_path.stat().st_size:
            findings.append(finding("SOURCE-W009", "warning", "structural", "intake", path, f"source size metadata is stale: {rel}", related_ids=[ident]))
        if source.get("mutable") is not False and source.get("origin") in {"official", "organizer_attachment"}:
            findings.append(finding("SOURCE-E010", "error", "semantic", "intake", path, f"official source must declare mutable=false: {ident}"))
        acquisition = source.get("acquisition")
        if source.get("origin") in {"official", "organizer_attachment"}:
            if not isinstance(acquisition, dict) or acquisition.get("provided_by_user") is not True:
                findings.append(finding("SOURCE-E011", "error", "semantic", "intake", path, f"official material must be supplied or explicitly identified by the user: {ident}"))
            elif acquisition.get("method") not in {"user_local_file", "user_supplied_url"}:
                findings.append(finding("SOURCE-E012", "error", "semantic", "intake", path, f"official material cannot come from autonomous search: {ident}"))
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
        required_hash_roles = {"formal_input", "claim_bearing_output"}
        allowed_roles = {"formal_input", "auxiliary_input"} if kind == "inputs" else {"claim_bearing_output", "intermediate_output", "diagnostic_output"}
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
            role = entry.get("evidence_role")
            if role not in allowed_roles:
                findings.append(finding("RUN-E016", "error", "structural", "computation", rel_path, f"missing or invalid evidence_role for {kind[:-1]}: {entry.get('path')}"))
                continue
            recorded_hash = entry.get("sha256")
            if role in required_hash_roles:
                if not nonempty(recorded_hash):
                    findings.append(finding("RUN-E015", "error", "execution", "computation", rel_path, f"required hash is missing for {role}: {entry.get('path')}"))
                elif recorded_hash != sha256(file_path):
                    findings.append(finding("RUN-E007", "error", "execution", "computation", rel_path, f"hash mismatch for {kind[:-1]}: {entry.get('path')}"))
            elif nonempty(recorded_hash) and recorded_hash != sha256(file_path):
                findings.append(finding("RUN-W007", "warning", "execution", "computation", rel_path, f"optional hash is stale for {role}: {entry.get('path')}"))
            if entry.get("size") != file_path.stat().st_size:
                findings.append(finding("RUN-W013", "warning", "execution", "computation", rel_path, f"size metadata is stale for {kind[:-1]}: {entry.get('path')}"))
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


def check_results(
    data: Any,
    root: Path,
    run_ids: set[str],
    run_output_roles: dict[str, dict[str, str]],
    path: str,
) -> list[Finding]:
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
        run_id = result.get("run_id")
        declared_outputs = run_output_roles.get(str(run_id), {})
        if rel not in declared_outputs:
            findings.append(finding("RESULT-E014", "error", "execution", "computation", path, f"{ident} locator is not a declared output of run {run_id}: {rel}", related_ids=[ident, str(run_id)]))
        elif declared_outputs[rel] != "claim_bearing_output":
            findings.append(finding("RESULT-E015", "error", "execution", "computation", path, f"{ident} locator must reference a claim_bearing_output: {rel}", related_ids=[ident, str(run_id)]))
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


def check_independent_review_package(data: Any, root: Path, path: str) -> list[Finding]:
    findings = check_envelope(data, "independent_review_package", "validation", path)
    if not isinstance(data, dict):
        return findings
    if data.get("conclusions_withheld") is not True:
        findings.append(finding("IREVIEW-E001", "error", "semantic", "validation", path, "independent review package must withhold the originating conclusions as far as practical"))
    for field in ("package_root", "review_skill_path", "review_request_path"):
        target = safe_project_path(root, data.get(field))
        if target is None or not target.exists():
            findings.append(finding("IREVIEW-E002", "error", "structural", "validation", path, f"independent review package is missing {field}: {data.get(field)}"))
    files = as_list(data.get("files"))
    roles = {str(item.get("role")) for item in files if isinstance(item, dict)}
    required_roles = {"official_input", "problem_contract", "model_contract", "computation_source", "run_record", "executed_output", "review_instruction"}
    missing_roles = sorted(required_roles - roles)
    if missing_roles:
        findings.append(finding("IREVIEW-E003", "error", "structural", "validation", path, f"independent review package misses roles: {', '.join(missing_roles)}"))
    for item in files:
        if not isinstance(item, dict):
            continue
        target = safe_project_path(root, item.get("path"))
        if target is None or not target.is_file() or target.stat().st_size == 0:
            findings.append(finding("IREVIEW-E004", "error", "structural", "validation", path, f"review package file is missing: {item.get('path')}"))
    selection = data.get("reviewer_selection")
    if not isinstance(selection, dict) or selection.get("status") != "user_confirmed":
        findings.append(finding("IREVIEW-E005", "error", "semantic", "validation", path, "the user must choose and confirm the reviewer before validation", gate_only=True))
    elif not all(nonempty(selection.get(field)) for field in ("selected_by", "reviewer", "task_ref")):
        findings.append(finding("IREVIEW-E006", "error", "structural", "validation", path, "confirmed reviewer selection lacks user, reviewer, or task reference"))
    return findings


def check_independent_review_result(data: Any, root: Path, path: str, package: Any) -> list[Finding]:
    findings = check_envelope(data, "independent_review_result", "validation", path)
    if not isinstance(data, dict):
        return findings
    expected_package = CONTRACT_PATHS["independent_review_package"]
    if data.get("package_manifest_path") != expected_package:
        findings.append(finding("IREVIEW-E007", "error", "structural", "validation", path, "independent review result names a different package manifest"))
    context = data.get("reviewer_context")
    if not isinstance(context, dict):
        return findings
    if context.get("selected_by_user") is not True:
        findings.append(finding("IREVIEW-E008", "error", "semantic", "validation", path, "independent reviewer was not selected by the user"))
    if context.get("different_conversation") is not True or context.get("reviewer_kind") == "same_context_model" or context.get("independence_grade") == "correlated_self_review":
        findings.append(finding("IREVIEW-E009", "error", "semantic", "validation", path, "same-context or correlated self-review cannot satisfy the independent review gate"))
    selection = package.get("reviewer_selection") if isinstance(package, dict) else None
    if isinstance(selection, dict):
        if selection.get("reviewer") != context.get("reviewer") or selection.get("task_ref") != context.get("task_ref"):
            findings.append(finding("IREVIEW-E010", "error", "structural", "validation", path, "imported reviewer identity does not match the user-confirmed selection"))
    raw_path = safe_project_path(root, data.get("raw_review_path"))
    if raw_path is None or not raw_path.is_file() or raw_path.stat().st_size == 0:
        findings.append(finding("IREVIEW-E011", "error", "structural", "validation", path, "raw independent review is missing"))
    if data.get("verdict") == "revision_requested":
        findings.append(finding("IREVIEW-E012", "error", "semantic", "model-design", path, "independent review requested revision; return to the earliest affected stage"))
    elif data.get("verdict") == "inconclusive":
        findings.append(finding("IREVIEW-E013", "error", "semantic", "validation", path, "independent review is inconclusive"))
    review = data.get("review")
    if not isinstance(review, dict) or review.get("decision") != "accepted":
        findings.append(finding("IREVIEW-E014", "error", "semantic", "validation", path, "imported independent review must be acknowledged at the user gate", gate_only=True))
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
        findings.append(finding("CLAIM-E006", "error", "semantic", "validation", path, f"{profile} profile requires a recorded independent logic pass", gate_only=True))
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
                findings.append(finding("CLAIM-E014", "error", "semantic", "validation", path, f"supported claim lacks accepted review: {ident}", related_ids=[ident], gate_only=True))
    return findings


def check_figures(data: Any, root: Path, result_ids: set[str], run_ids: set[str], path: str, profile: str) -> list[Finding]:
    findings = check_envelope(data, "figure_manifest", "paper", path)
    if not isinstance(data, dict):
        return findings
    figures = data.get("figures")
    findings.extend(require_fields(figures, ("kind", "purpose", "path", "caption_claims", "visual_review"), ("figure_id",), "FIGURE", "paper", path))
    for figure in as_list(figures):
        if not isinstance(figure, dict):
            continue
        ident = item_id(figure, "figure_id")
        kind = figure.get("kind")
        figure_path = safe_project_path(root, figure.get("path"))
        if figure_path is None or not figure_path.is_file() or figure_path.stat().st_size == 0:
            findings.append(finding("FIGURE-E010", "error", "visual", "paper", path, f"missing or empty figure file: {figure.get('path')}", related_ids=[ident]))
        elif nonempty(figure.get("sha256")) and figure.get("sha256") != sha256(figure_path):
            findings.append(finding("FIGURE-W011", "warning", "structural", "paper", path, f"figure changed since its manifest entry was recorded: {figure.get('path')}", related_ids=[ident]))
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
            findings.append(finding("FIGURE-E009", severity, "visual", "paper", path, f"figure lacks accepted visual review: {ident}", related_ids=[ident], gate_only=severity == "error"))
    return findings


def check_delivery(data: Any, root: Path, path: str, profile: str) -> list[Finding]:
    findings = check_envelope(data, "delivery_manifest", "delivery", path)
    if not isinstance(data, dict):
        return findings
    if data.get("profile") != profile:
        findings.append(finding("DELIVERY-E001", "error", "structural", "delivery", path, "delivery profile does not match requested profile"))
    source_policy = data.get("source_policy")
    if not isinstance(source_policy, dict) or source_policy.get("mode") != "user_supplied_only" or source_policy.get("network_lookup_performed") is not False:
        findings.append(finding("DELIVERY-E013", "error", "semantic", "delivery", path, "delivery compliance review must use user-supplied materials only and must not perform autonomous network lookup"))
    elif as_list(source_policy.get("missing_user_materials")):
        findings.append(finding("DELIVERY-E014", "error", "semantic", "delivery", path, "delivery is blocked_missing_user_material; request the listed materials from the user"))
    deliverables = data.get("deliverables")
    required_roles = {"final_pdf", "editable_latex_source", "computation_source"}
    if not isinstance(deliverables, dict) or not required_roles.issubset(deliverables):
        findings.append(finding("DELIVERY-E015", "error", "structural", "delivery", path, "delivery must declare final PDF, editable LaTeX source, and computation source"))
    else:
        for role in sorted(required_roles):
            item = deliverables.get(role)
            if not isinstance(item, dict):
                continue
            artifact_path = safe_project_path(root, item.get("path"))
            entrypoint = safe_project_path(root, item.get("entrypoint"))
            if artifact_path is None or not artifact_path.exists() or entrypoint is None or not entrypoint.is_file():
                findings.append(finding("DELIVERY-E016", "error", "structural", "delivery", path, f"declared {role} or its entrypoint is missing"))
            if role != "final_pdf" and item.get("editable") is not True:
                findings.append(finding("DELIVERY-E017", "error", "semantic", "delivery", path, f"{role} must be delivered in editable form"))

    files = data.get("files")
    findings.extend(require_fields(files, ("path", "role", "size"), ("path",), "DELIVERY", "delivery", path))
    for item in as_list(files):
        if not isinstance(item, dict):
            continue
        rel = item.get("path")
        file_path = safe_project_path(root, rel)
        if file_path is None or not file_path.is_file() or file_path.stat().st_size == 0:
            findings.append(finding("DELIVERY-E006", "error", "structural", "delivery", path, f"missing or empty delivery file: {rel}"))
            continue
        recorded_hash = item.get("sha256")
        if item.get("role") == "final_pdf":
            if not nonempty(recorded_hash) or recorded_hash != sha256(file_path):
                findings.append(finding("DELIVERY-E007", "error", "structural", "delivery", path, f"final PDF hash is missing or mismatched: {rel}"))
        elif nonempty(recorded_hash) and recorded_hash != sha256(file_path):
            findings.append(finding("DELIVERY-W007", "warning", "structural", "delivery", path, f"optional delivery hash is stale: {rel}"))
        if item.get("size") != file_path.stat().st_size:
            findings.append(finding("DELIVERY-W008", "warning", "structural", "delivery", path, f"delivery size metadata is stale: {rel}"))
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
        findings.append(finding("DELIVERY-E011", "error", "semantic", "delivery", path, "final human review must be accepted", gate_only=True))
    return findings


def check_bound_artifact(root: Path, artifact: Any, stage: str, path: str, rule_prefix: str) -> list[Finding]:
    if not isinstance(artifact, dict):
        return [finding(f"{rule_prefix}-E001", "error", "structural", stage, path, "artifact binding must be an object")]
    rel = artifact.get("path")
    file_path = safe_project_path(root, rel)
    if file_path is None or not file_path.is_file() or file_path.stat().st_size == 0:
        return [finding(f"{rule_prefix}-E002", "error", "structural", stage, path, f"bound artifact is missing or empty: {rel}")]
    if artifact.get("sha256") != sha256(file_path):
        return [finding(f"{rule_prefix}-E003", "error", "structural", stage, path, f"bound artifact hash mismatch: {rel}")]
    return []


def check_paper_plan(
    data: Any,
    path: str,
    subproblem_ids: set[str],
    claim_ids: set[str],
    result_ids: set[str],
    figure_ids: set[str],
    known_evidence_ids: set[str],
    profile: str,
) -> list[Finding]:
    findings = check_envelope(data, "paper_plan", "paper", path)
    if not isinstance(data, dict):
        return findings
    references = as_list(data.get("reference_reviews"))
    if profile == "strict" and not references:
        findings.append(finding("PPLAN-E001", "error", "semantic", "paper", path, "strict profile requires at least one quality-reference review"))
    matrix = as_list(data.get("claims_evidence_matrix"))
    matrix_claim_ids = ids(matrix, "claim_id")
    for row in matrix:
        if not isinstance(row, dict):
            continue
        claim_id = item_id(row, "claim_id")
        if claim_id not in claim_ids:
            findings.append(finding("PPLAN-E002", "error", "structural", "paper", path, f"claims-evidence matrix names unknown claim: {claim_id}", related_ids=[claim_id]))
        if row.get("subproblem_id") not in subproblem_ids:
            findings.append(finding("PPLAN-E003", "error", "structural", "paper", path, f"matrix row names unknown subproblem: {row.get('subproblem_id')}", related_ids=[claim_id]))
        for evidence_id in as_list(row.get("evidence_ids")):
            if evidence_id not in known_evidence_ids:
                findings.append(finding("PPLAN-E004", "error", "structural", "paper", path, f"matrix row names unknown evidence: {evidence_id}", related_ids=[claim_id, str(evidence_id)]))
    missing_claims = sorted(claim_ids - matrix_claim_ids)
    if missing_claims:
        findings.append(finding("PPLAN-E005", "error", "semantic", "paper", path, f"claims missing from claims-evidence matrix: {', '.join(missing_claims)}", related_ids=missing_claims))

    chains = as_list(data.get("question_argument_chains"))
    chain_subproblems = ids(chains, "subproblem_id")
    missing_questions = sorted(subproblem_ids - chain_subproblems)
    if missing_questions:
        findings.append(finding("PPLAN-E006", "error", "semantic", "paper", path, f"subproblems missing complete argument chains: {', '.join(missing_questions)}", related_ids=missing_questions))
    for chain in chains:
        if not isinstance(chain, dict):
            continue
        subproblem = item_id(chain, "subproblem_id")
        if subproblem not in subproblem_ids:
            findings.append(finding("PPLAN-E007", "error", "structural", "paper", path, f"argument chain names unknown subproblem: {subproblem}", related_ids=[subproblem]))
        layers = chain.get("layers")
        if not isinstance(layers, dict):
            continue
        missing_layers = sorted(PAPER_LAYER_NAMES - set(layers))
        if missing_layers:
            findings.append(finding("PPLAN-E008", "error", "semantic", "paper", path, f"{subproblem} argument chain misses layers: {', '.join(missing_layers)}", related_ids=[subproblem]))
        for layer_name, layer in layers.items():
            if not isinstance(layer, dict):
                continue
            layer_ids = as_list(layer.get("evidence_ids"))
            if layer.get("status") == "included" and not layer_ids:
                findings.append(finding("PPLAN-E009", "error", "semantic", "paper", path, f"included layer lacks evidence IDs: {subproblem}/{layer_name}", related_ids=[subproblem]))
            if layer.get("status") == "not_applicable" and not nonempty(layer.get("rationale")):
                findings.append(finding("PPLAN-E010", "error", "semantic", "paper", path, f"not_applicable layer lacks rationale: {subproblem}/{layer_name}", related_ids=[subproblem]))
            for evidence_id in layer_ids:
                if evidence_id not in known_evidence_ids:
                    findings.append(finding("PPLAN-E011", "error", "structural", "paper", path, f"argument layer names unknown evidence: {evidence_id}", related_ids=[subproblem, str(evidence_id)]))

    plans = as_list(data.get("figure_plan"))
    planned_ids = ids(plans, "figure_id")
    for plan in plans:
        if not isinstance(plan, dict):
            continue
        figure_id = item_id(plan, "figure_id")
        if plan.get("required") is True and figure_id not in figure_ids:
            findings.append(finding("PPLAN-E012", "error", "visual", "paper", path, f"required planned figure was not produced: {figure_id}", related_ids=[figure_id]))
        for claim_id in as_list(plan.get("claim_ids")):
            if claim_id not in claim_ids:
                findings.append(finding("PPLAN-E013", "error", "structural", "paper", path, f"figure plan names unknown claim: {claim_id}", related_ids=[figure_id, str(claim_id)]))
        for result_id in as_list(plan.get("result_ids")):
            if result_id not in result_ids:
                findings.append(finding("PPLAN-E014", "error", "structural", "paper", path, f"figure plan names unknown result: {result_id}", related_ids=[figure_id, str(result_id)]))
        if plan.get("kind") != "conceptual" and (not as_list(plan.get("claim_ids")) or not as_list(plan.get("result_ids"))):
            findings.append(finding("PPLAN-E015", "error", "semantic", "paper", path, f"quantitative figure plan must explain a claim with indexed results: {figure_id}", related_ids=[figure_id]))
    unplanned = sorted(figure_ids - planned_ids)
    if unplanned:
        findings.append(finding("PPLAN-E016", "error", "semantic", "paper", path, f"produced figures missing from paper plan: {', '.join(unplanned)}", related_ids=unplanned))
    return findings


def check_paper_quality(
    data: Any,
    root: Path,
    path: str,
    subproblem_ids: set[str],
    known_evidence_ids: set[str],
    profile: str,
) -> list[Finding]:
    findings = check_envelope(data, "paper_quality_report", "paper", path)
    if not isinstance(data, dict):
        return findings
    paper = data.get("paper_artifact")
    findings.extend(check_bound_artifact(root, paper, "paper", path, "PQUALITY"))
    bound_hash = paper.get("sha256") if isinstance(paper, dict) else None
    bound_path = paper.get("path") if isinstance(paper, dict) else None
    content = data.get("content_review")
    layout = data.get("layout_review")
    final_qa = data.get("final_qa")
    for name, review in (("content", content), ("layout", layout), ("final", final_qa)):
        if not isinstance(review, dict):
            continue
        if review.get("decision") == "accepted" and (not nonempty(review.get("reviewer")) or not nonempty(review.get("reviewed_at"))):
            findings.append(finding("PQUALITY-E012", "error", "semantic", "paper", path, f"accepted {name} review lacks reviewer or review time"))
        artifact = review.get("artifact")
        if isinstance(artifact, dict) and (artifact.get("path") != bound_path or artifact.get("sha256") != bound_hash):
            findings.append(finding("PQUALITY-E004", "error", "structural", "paper", path, f"{name} review is bound to a different paper version"))
    if isinstance(content, dict):
        for dimension in ("abstract_synthesis", "conclusion_directness", "internal_metadata_separation", "reference_style_transfer"):
            item = content.get(dimension)
            if isinstance(item, dict) and item.get("status") == "fail":
                findings.append(finding("PQUALITY-E015", "error", "semantic", "paper", path, f"content review failed: {dimension}"))
        reviewed_questions = ids(content.get("questions"), "subproblem_id")
        missing = sorted(subproblem_ids - reviewed_questions)
        if missing:
            findings.append(finding("PQUALITY-E005", "error", "semantic", "paper", path, f"content review misses subproblems: {', '.join(missing)}", related_ids=missing))
        for question in as_list(content.get("questions")):
            if not isinstance(question, dict):
                continue
            subproblem = item_id(question, "subproblem_id")
            for dimension in (
                "argument_chain",
                "mechanism_explanation",
                "derivation",
                "result_interpretation",
                "reader_facing_language",
                "numerical_presentation",
                "validation_strength",
                "limitations",
            ):
                item = question.get(dimension)
                if not isinstance(item, dict):
                    continue
                if item.get("status") == "fail":
                    findings.append(finding("PQUALITY-E006", "error", "semantic", "paper", path, f"content review failed: {subproblem}/{dimension}", related_ids=[subproblem]))
                for evidence_id in as_list(item.get("evidence_ids")):
                    if evidence_id not in known_evidence_ids:
                        findings.append(finding("PQUALITY-E007", "error", "structural", "paper", path, f"content review names unknown evidence: {evidence_id}", related_ids=[subproblem, str(evidence_id)]))
    if isinstance(layout, dict):
        page_count = layout.get("page_count")
        pages = {page for page in as_list(layout.get("rendered_pages")) if isinstance(page, int)}
        if (profile == "strict" or data.get("paper_status") == "final") and isinstance(page_count, int) and pages != set(range(1, page_count + 1)):
            findings.append(finding("PQUALITY-E008", "error", "visual", "paper", path, "strict or final layout review must record visual inspection of every PDF page"))
        if any(isinstance(check, dict) and check.get("status") == "fail" for check in as_list(layout.get("checks"))):
            findings.append(finding("PQUALITY-E009", "error", "visual", "paper", path, "layout review contains failed checks"))
    issues = as_list(data.get("open_issues"))
    if data.get("paper_status") == "final":
        for name, review in (("content", content), ("layout", layout), ("final QA", final_qa)):
            if not isinstance(review, dict) or review.get("decision") != "accepted":
                findings.append(finding("PQUALITY-E010", "error", "semantic", "paper", path, f"final paper lacks accepted {name} review", gate_only=True))
        open_p0 = [item_id(issue, "issue_id") for issue in issues if isinstance(issue, dict) and issue.get("severity") == "P0" and issue.get("status") == "open"]
        if open_p0:
            findings.append(finding("PQUALITY-E011", "error", "semantic", "paper", path, f"final paper has open P0 issues: {', '.join(open_p0)}", related_ids=open_p0))
        if isinstance(content, dict) and content.get("reviewer_kind") == "same_context_model":
            findings.append(finding("PQUALITY-E013", "error", "semantic", "paper", path, "same-context content self-review cannot finalize the reader-facing paper", gate_only=True))
        if isinstance(final_qa, dict) and final_qa.get("reviewer_kind") == "same_context_model":
            findings.append(finding("PQUALITY-E014", "error", "semantic", "paper", path, "same-context final QA cannot finalize the paper", gate_only=True))
    return findings


def check_paper_traceability(data: Any, path: str, claim_ids: set[str], result_ids: set[str]) -> list[Finding]:
    findings = check_envelope(data, "paper_traceability", "paper", path)
    if not isinstance(data, dict):
        return findings
    if data.get("visible_id_policy") != "prohibited":
        findings.append(finding("PTRACE-E001", "error", "semantic", "paper", path, "paper traceability must keep internal IDs out of visible content"))
    for entry in as_list(data.get("entries")):
        if not isinstance(entry, dict):
            continue
        if entry.get("render_policy") != "sidecar_only":
            findings.append(finding("PTRACE-E002", "error", "semantic", "paper", path, f"traceability entry is not sidecar-only: {entry.get('anchor')}"))
        for claim_id in as_list(entry.get("claim_ids")):
            if claim_id not in claim_ids:
                findings.append(finding("PTRACE-E003", "error", "structural", "paper", path, f"traceability entry names unknown claim: {claim_id}"))
        for result_id in as_list(entry.get("result_ids")):
            if result_id not in result_ids:
                findings.append(finding("PTRACE-E004", "error", "structural", "paper", path, f"traceability entry names unknown result: {result_id}"))
    return findings


def check_paper_visible_text(data: Any, root: Path, path: str, paper_quality: Any) -> list[Finding]:
    findings = check_envelope(data, "paper_visible_text_report", "paper", path)
    if not isinstance(data, dict):
        return findings
    artifact = data.get("paper_artifact")
    findings.extend(check_bound_artifact(root, artifact, "paper", path, "PTEXT"))
    quality_artifact = paper_quality.get("paper_artifact") if isinstance(paper_quality, dict) else None
    if isinstance(artifact, dict) and isinstance(quality_artifact, dict) and artifact != quality_artifact:
        findings.append(finding("PTEXT-E004", "error", "structural", "paper", path, "visible-text report is bound to a different PDF than the paper quality report"))
    if as_list(data.get("blocking_matches")):
        findings.append(finding("PTEXT-E005", "error", "semantic", "paper", path, "final PDF exposes workflow metadata, internal IDs, evidence states, or local paths"))
    open_flags = [flag for flag in as_list(data.get("review_flags")) if isinstance(flag, dict) and flag.get("resolution_status") == "open"]
    if open_flags:
        findings.append(finding("PTEXT-E006", "error", "semantic", "paper", path, "visible-text report has unresolved numerical-presentation flags"))
    if isinstance(paper_quality, dict) and paper_quality.get("paper_status") == "final":
        review = data.get("review")
        if not isinstance(review, dict) or review.get("decision") != "accepted":
            findings.append(finding("PTEXT-E007", "error", "semantic", "paper", path, "final visible-text report requires reader-facing review", gate_only=True))
    return findings


def check_latex_template(
    data: Any,
    root: Path,
    path: str,
    subproblem_ids: set[str],
    paper_quality: Any,
    through_stage: str,
) -> list[Finding]:
    findings = check_envelope(data, "latex_template_manifest", "paper", path)
    if not isinstance(data, dict):
        return findings
    required_files = as_list(data.get("required_files"))
    for rel in required_files:
        file_path = safe_project_path(root, rel)
        if file_path is None or not file_path.is_file() or file_path.stat().st_size == 0:
            findings.append(finding("LATEX-E001", "error", "structural", "paper", path, f"required LaTeX file is missing or empty: {rel}"))
    main_rel = data.get("main_path")
    main_path = safe_project_path(root, main_rel)
    main_text = ""
    if main_path is None or not main_path.is_file():
        findings.append(finding("LATEX-E002", "error", "structural", "paper", path, f"LaTeX main file is missing: {main_rel}"))
    else:
        main_text = main_path.read_text(encoding="utf-8", errors="replace")
    section_files = set(str(value) for value in as_list(data.get("section_files")))
    mappings = as_list(data.get("subproblem_sections"))
    mapped_ids: set[str] = set()
    mapped_paths: set[str] = set()
    for mapping in mappings:
        if not isinstance(mapping, dict):
            continue
        subproblem_id = item_id(mapping, "subproblem_id")
        rel = mapping.get("path")
        if subproblem_id in mapped_ids:
            findings.append(finding("LATEX-E003", "error", "structural", "paper", path, f"duplicate LaTeX subproblem mapping: {subproblem_id}", related_ids=[subproblem_id]))
        mapped_ids.add(subproblem_id)
        mapped_paths.add(str(rel))
        if rel not in section_files:
            findings.append(finding("LATEX-E004", "error", "structural", "paper", path, f"mapped subproblem section is absent from section_files: {rel}", related_ids=[subproblem_id]))
        rel_path = safe_project_path(root, rel)
        if rel_path is None or not rel_path.is_file():
            findings.append(finding("LATEX-E005", "error", "structural", "paper", path, f"mapped subproblem section is missing: {rel}", related_ids=[subproblem_id]))
        if nonempty(rel) and main_text:
            input_target = str(rel)
            if input_target.startswith("paper/"):
                input_target = input_target[len("paper/") :]
            input_target = input_target[:-4] if input_target.endswith(".tex") else input_target
            if f"\\input{{{input_target}}}" not in main_text:
                findings.append(finding("LATEX-E006", "error", "structural", "paper", path, f"main.tex does not include mapped subproblem section: {rel}", related_ids=[subproblem_id]))
    missing = sorted(subproblem_ids - mapped_ids)
    extra = sorted(mapped_ids - subproblem_ids)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if extra:
            details.append(f"unknown {', '.join(extra)}")
        findings.append(finding("LATEX-E007", "error", "semantic", "paper", path, f"LaTeX subproblem mapping mismatch: {'; '.join(details)}", related_ids=[*missing, *extra]))

    quality_status = paper_quality.get("paper_status") if isinstance(paper_quality, dict) else None
    if quality_status == "final":
        markers = [str(value) for value in as_list(data.get("placeholder_markers")) if nonempty(value)]
        for rel in required_files:
            if not str(rel).endswith(".tex"):
                continue
            source = safe_project_path(root, rel)
            if source is None or not source.is_file():
                continue
            text = source.read_text(encoding="utf-8", errors="replace")
            present = [marker for marker in markers if marker in text]
            if present:
                findings.append(finding("LATEX-E008", "error", "semantic", "paper", path, f"final paper source still contains placeholder markers in {rel}: {', '.join(present)}"))
    if through_stage == "delivery" and data.get("official_compliance") != "verified_against_current_rules":
        findings.append(finding("LATEX-E009", "error", "visual", "delivery", path, "delivery requires the LaTeX scaffold to be reviewed against the current official rules", gate_only=True))
    return findings


def check_revision_log(data: Any, root: Path, path: str, paper_artifact: Any, issues: Any) -> list[Finding]:
    findings = check_envelope(data, "paper_revision_log", "paper", path)
    if not isinstance(data, dict):
        return findings
    snapshots: list[tuple[str, Any]] = [("initial_snapshot", data.get("initial_snapshot"))]
    revisions = as_list(data.get("revisions"))
    issue_items = {item_id(issue, "issue_id"): issue for issue in as_list(issues) if isinstance(issue, dict)}
    issue_ids = set(issue_items)
    verified_issue_ids: set[str] = set()
    seen: set[str] = set()
    previous_output: Any = data.get("initial_snapshot")
    for index, revision in enumerate(revisions):
        if not isinstance(revision, dict):
            continue
        revision_id = item_id(revision, "revision_id")
        if revision_id in seen:
            findings.append(finding("PREVISION-E001", "error", "structural", "paper", path, f"duplicate revision ID: {revision_id}", related_ids=[revision_id]))
        seen.add(revision_id)
        if revision.get("input") != previous_output:
            findings.append(finding("PREVISION-E002", "error", "structural", "paper", path, f"revision input does not match previous snapshot: {revision_id}", related_ids=[revision_id]))
        snapshots.extend(((f"revisions/{index}/input", revision.get("input")), (f"revisions/{index}/output", revision.get("output"))))
        previous_output = revision.get("output")
        for issue_id in as_list(revision.get("issue_ids")):
            if issue_id not in issue_ids:
                findings.append(finding("PREVISION-E003", "error", "structural", "paper", path, f"revision names unknown issue: {issue_id}", related_ids=[revision_id, str(issue_id)]))
            elif isinstance(revision.get("verification"), dict) and revision["verification"].get("decision") == "accepted":
                verified_issue_ids.add(str(issue_id))
    for label, snapshot in snapshots:
        for item in check_bound_artifact(root, snapshot, "paper", path, "PREVISION"):
            findings.append(finding(item.rule_id, item.severity, item.evidence_type, item.owning_stage, item.path, f"{label}: {item.message}"))
    if isinstance(paper_artifact, dict) and previous_output != paper_artifact:
        findings.append(finding("PREVISION-E004", "error", "structural", "paper", path, "latest revision snapshot does not match the paper quality report artifact"))
    unverified_closed = sorted(
        issue_id
        for issue_id, issue in issue_items.items()
        if issue.get("status") == "closed" and issue_id not in verified_issue_ids
    )
    if unverified_closed:
        findings.append(finding("PREVISION-E005", "error", "semantic", "paper", path, f"closed issues lack an accepted revision verification: {', '.join(unverified_closed)}", related_ids=unverified_closed))
    return findings


def check_compile_receipt(data: Any, root: Path, path: str, quality_report: Any, latex_template: Any, delivery: Any, profile: str) -> list[Finding]:
    findings = check_envelope(data, "compile_receipt", "delivery", path)
    if not isinstance(data, dict):
        return findings
    attempts = {item_id(item, "attempt_id"): item for item in as_list(data.get("attempts")) if isinstance(item, dict)}
    selected_id = data.get("selected_attempt_id")
    selected = attempts.get(str(selected_id))
    if selected is None:
        findings.append(finding("COMPILE-E001", "error", "execution", "delivery", path, f"selected compile attempt does not exist: {selected_id}"))
        return findings
    pdf_binding = {"path": selected.get("pdf_path"), "sha256": selected.get("pdf_sha256")}
    findings.extend(check_bound_artifact(root, pdf_binding, "delivery", path, "COMPILE"))
    log_path = safe_project_path(root, selected.get("log_path"))
    if log_path is None or not log_path.is_file():
        findings.append(finding("COMPILE-E004", "error", "execution", "delivery", path, "selected compile log is missing"))
    if selected.get("exit_code") != 0:
        findings.append(finding("COMPILE-E005", "error", "execution", "delivery", path, "selected compile attempt did not exit successfully"))
    if profile == "strict" and (selected.get("font_check") != "pass" or selected.get("glyph_check") != "pass"):
        findings.append(finding("COMPILE-E006", "error", "visual", "delivery", path, "strict delivery requires passing font and missing-glyph checks"))
    if isinstance(latex_template, dict) and str(selected.get("engine", "")).casefold() != str(latex_template.get("engine", "")).casefold():
        findings.append(finding("COMPILE-E014", "error", "execution", "delivery", path, "selected compile engine differs from the LaTeX template manifest"))
    binding = data.get("layout_review_binding")
    if isinstance(binding, dict):
        quality_path = safe_project_path(root, binding.get("quality_report_path"))
        if quality_path is None or not quality_path.is_file():
            findings.append(finding("COMPILE-E007", "error", "structural", "delivery", path, "layout-review binding does not point to the current paper quality report"))
        if binding.get("pdf_sha256") != selected.get("pdf_sha256"):
            findings.append(finding("COMPILE-E008", "error", "structural", "delivery", path, "layout-review binding names a different PDF version"))
    if isinstance(quality_report, dict):
        if quality_report.get("paper_status") != "final":
            findings.append(finding("COMPILE-E013", "error", "semantic", "delivery", path, "delivery requires a paper quality report with paper_status=final"))
        paper = quality_report.get("paper_artifact")
        layout = quality_report.get("layout_review")
        if isinstance(paper, dict) and (paper.get("path") != selected.get("pdf_path") or paper.get("sha256") != selected.get("pdf_sha256")):
            findings.append(finding("COMPILE-E009", "error", "structural", "delivery", path, "selected compile PDF differs from the reviewed paper artifact"))
        if isinstance(layout, dict) and layout.get("page_count") != selected.get("page_count"):
            findings.append(finding("COMPILE-E010", "error", "visual", "delivery", path, "compile receipt page count differs from layout review"))
    if isinstance(delivery, dict):
        if delivery.get("compile_receipt_path") != path:
            findings.append(finding("COMPILE-E011", "error", "structural", "delivery", path, "delivery manifest does not point to this compile receipt"))
        summary = delivery.get("compile")
        if isinstance(summary, dict) and (summary.get("exit_code") != selected.get("exit_code") or summary.get("page_count") != selected.get("page_count")):
            findings.append(finding("COMPILE-E012", "error", "execution", "delivery", path, "delivery compile summary disagrees with selected compile attempt"))
    return findings


def stage_scope_paths(root: Path, stage: str) -> list[str]:
    mapping = {
        "intake": [CONTRACT_PATHS["sources"]],
        "problem-analysis": [CONTRACT_PATHS["facts"], CONTRACT_PATHS["capabilities"]],
        "model-design": [CONTRACT_PATHS["model"], CONTRACT_PATHS["cross_question"]],
        "computation": [CONTRACT_PATHS["results"]],
        "validation": [CONTRACT_PATHS["independent_review_package"], CONTRACT_PATHS["independent_review_result"], CONTRACT_PATHS["claims"]],
        "paper": [CONTRACT_PATHS["figures"], *(CONTRACT_PATHS[name] for name in PAPER_CONTRACTS)],
        "delivery": [CONTRACT_PATHS["delivery"], CONTRACT_PATHS["compile_receipt"]],
    }
    paths = list(mapping[stage])
    if stage == "computation":
        paths.extend(path.relative_to(root).as_posix() for path in discover_run_manifests(root))
    return paths


def check_decision_log(root: Path, state: Any) -> list[Finding]:
    path = ".cumcm/decisions.jsonl"
    log_path = root / path
    if not log_path.is_file():
        return [finding("DECISION-E001", "error", "semantic", "intake", path, "v0.4 project has no append-only decision log", gate_only=True)]
    findings: list[Finding] = []
    events: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for line_number, raw in enumerate(log_path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError as exc:
            findings.append(finding("DECISION-E002", "error", "structural", "intake", path, f"invalid JSON on line {line_number}: {exc}"))
            continue
        if not isinstance(event, dict):
            findings.append(finding("DECISION-E003", "error", "structural", "intake", path, f"decision event on line {line_number} is not an object"))
            continue
        decision_id = item_id(event, "decision_id")
        if not decision_id or decision_id in seen_ids:
            findings.append(finding("DECISION-E004", "error", "structural", "intake", path, f"missing or duplicate decision_id on line {line_number}: {decision_id}"))
        seen_ids.add(decision_id)
        if event.get("stage") not in STAGES or event.get("decision") not in {"accepted", "revision_requested"}:
            findings.append(finding("DECISION-E007", "error", "structural", "intake", path, f"invalid stage or decision on line {line_number}", related_ids=[decision_id]))
        for required_field in ("reviewer", "task_turn_ref", "user_visible_summary", "decided_at"):
            if not nonempty(event.get(required_field)):
                findings.append(finding("DECISION-E011", "error", "structural", "intake", path, f"decision event lacks {required_field} on line {line_number}", related_ids=[decision_id]))
        if not isinstance(event.get("scope"), list) or not event.get("scope"):
            findings.append(finding("DECISION-E012", "error", "structural", "intake", path, f"decision event has no artifact scope on line {line_number}", related_ids=[decision_id]))
        else:
            for entry in event["scope"]:
                if not isinstance(entry, dict) or safe_project_path(root, entry.get("path")) is None or not re.fullmatch(r"[0-9a-f]{64}", str(entry.get("sha256", ""))):
                    findings.append(finding("DECISION-E013", "error", "structural", "intake", path, f"decision event has an invalid scope entry on line {line_number}", related_ids=[decision_id]))
        events.append(event)
    latest: dict[str, dict[str, Any]] = {}
    for event in events:
        if event.get("stage") in STAGES:
            latest[str(event["stage"])] = event
    state_map = state.get("stages", {}) if isinstance(state, dict) else {}
    for stage in STAGES:
        if state_map.get(stage) != "passed":
            continue
        event = latest.get(stage)
        if event is None or event.get("decision") != "accepted":
            findings.append(finding("DECISION-E008", "error", "semantic", stage, path, f"passed stage lacks a latest accepted decision: {stage}", gate_only=True))
            continue
        scope = {entry.get("path"): entry.get("sha256") for entry in as_list(event.get("scope")) if isinstance(entry, dict)}
        for rel in stage_scope_paths(root, stage):
            artifact = safe_project_path(root, rel)
            if artifact is None or not artifact.is_file():
                findings.append(finding("DECISION-E009", "error", "structural", stage, path, f"decision scope target is missing: {rel}"))
            elif scope.get(rel) != sha256(artifact):
                findings.append(finding("DECISION-E010", "error", "structural", stage, path, f"accepted decision is stale or does not cover current artifact: {rel}"))
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
        "independent_review_package": "validation",
        "independent_review_result": "validation",
        "claims": "validation",
        "figures": "paper",
        "paper_plan": "paper",
        "latex_template": "paper",
        "paper_quality": "paper",
        "paper_revisions": "paper",
        "paper_traceability": "paper",
        "paper_visible_text": "paper",
        "delivery": "delivery",
        "compile_receipt": "delivery",
    }[name]


def check_project(root: Path, stage: str, profile: str, gate_mode: str = "enforce") -> tuple[list[Finding], dict[str, Any]]:
    if stage not in STAGES:
        raise ValueError(f"unknown stage: {stage}")
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    if gate_mode not in GATE_MODES:
        raise ValueError(f"unknown gate mode: {gate_mode}")
    state_preview, _ = read_json(root / CONTRACT_PATHS["state"])
    workflow_version = state_preview.get("workflow_version") if isinstance(state_preview, dict) else None
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
    claim_ids: set[str] = set()

    if "state" in contracts:
        findings.extend(check_schema(contracts["state"], "state", "intake", CONTRACT_PATHS["state"]))
        findings.extend(check_state(contracts["state"], CONTRACT_PATHS["state"]))
    for name, contract in contracts.items():
        if isinstance(contract, dict) and contract.get("schema_version") != WORKFLOW_VERSION:
            findings.append(finding("PROJECT-E004", "error", "structural", owning_stage_for_contract(name), CONTRACT_PATHS[name], "contract schema_version must be 0.4.0"))
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
    run_output_roles: dict[str, dict[str, str]] = {}
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
                run_output_roles[run["run_id"]] = {
                    str(entry.get("path")): str(entry.get("evidence_role"))
                    for entry in as_list(run.get("outputs"))
                    if isinstance(entry, dict) and nonempty(entry.get("path"))
                }
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
        findings.extend(check_results(contracts["results"], root, run_ids, run_output_roles, CONTRACT_PATHS["results"]))
        result_ids = ids(contracts["results"].get("results"), "result_id") if isinstance(contracts["results"], dict) else set()
        if "capabilities" in contracts and isinstance(contracts["capabilities"], dict):
            for capability in as_list(contracts["capabilities"].get("capabilities")):
                if not isinstance(capability, dict):
                    continue
                capability_id = item_id(capability, "capability_id")
                for result_id in as_list(capability.get("result_ids")):
                    if result_id not in result_ids:
                        findings.append(finding("RESULT-E013", "error", "structural", "computation", CONTRACT_PATHS["capabilities"], f"{capability_id} expects unknown result: {result_id}", related_ids=[capability_id, str(result_id)]))
    if "independent_review_package" in contracts:
        findings.extend(check_schema(contracts["independent_review_package"], "independent_review_package", "validation", CONTRACT_PATHS["independent_review_package"]))
        findings.extend(check_independent_review_package(contracts["independent_review_package"], root, CONTRACT_PATHS["independent_review_package"]))
    if "independent_review_result" in contracts:
        findings.extend(check_schema(contracts["independent_review_result"], "independent_review_result", "validation", CONTRACT_PATHS["independent_review_result"]))
        findings.extend(check_independent_review_result(contracts["independent_review_result"], root, CONTRACT_PATHS["independent_review_result"], contracts.get("independent_review_package")))
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
        if isinstance(contracts["claims"], dict):
            claim_ids = ids(contracts["claims"].get("claims"), "claim_id")
    known_evidence_ids = set().union(fact_ids, model_ids, run_ids, result_ids, figure_ids, claim_ids)
    if "paper_plan" in contracts:
        findings.extend(check_schema(contracts["paper_plan"], "paper_plan", "paper", CONTRACT_PATHS["paper_plan"]))
        findings.extend(check_paper_plan(contracts["paper_plan"], CONTRACT_PATHS["paper_plan"], subproblem_ids, claim_ids, result_ids, figure_ids, known_evidence_ids, profile))
    if "paper_quality" in contracts:
        findings.extend(check_schema(contracts["paper_quality"], "paper_quality", "paper", CONTRACT_PATHS["paper_quality"]))
        findings.extend(check_paper_quality(contracts["paper_quality"], root, CONTRACT_PATHS["paper_quality"], subproblem_ids, known_evidence_ids, profile))
    if "latex_template" in contracts:
        findings.extend(check_schema(contracts["latex_template"], "latex_template", "paper", CONTRACT_PATHS["latex_template"]))
        findings.extend(check_latex_template(contracts["latex_template"], root, CONTRACT_PATHS["latex_template"], subproblem_ids, contracts.get("paper_quality"), stage))
    if "paper_revisions" in contracts:
        findings.extend(check_schema(contracts["paper_revisions"], "paper_revisions", "paper", CONTRACT_PATHS["paper_revisions"]))
        quality = contracts.get("paper_quality")
        paper_artifact = quality.get("paper_artifact") if isinstance(quality, dict) else None
        issues = quality.get("open_issues") if isinstance(quality, dict) else []
        findings.extend(check_revision_log(contracts["paper_revisions"], root, CONTRACT_PATHS["paper_revisions"], paper_artifact, issues))
    if "paper_traceability" in contracts:
        findings.extend(check_schema(contracts["paper_traceability"], "paper_traceability", "paper", CONTRACT_PATHS["paper_traceability"]))
        findings.extend(check_paper_traceability(contracts["paper_traceability"], CONTRACT_PATHS["paper_traceability"], claim_ids, result_ids))
    if "paper_visible_text" in contracts:
        findings.extend(check_schema(contracts["paper_visible_text"], "paper_visible_text", "paper", CONTRACT_PATHS["paper_visible_text"]))
        findings.extend(check_paper_visible_text(contracts["paper_visible_text"], root, CONTRACT_PATHS["paper_visible_text"], contracts.get("paper_quality")))
    if "delivery" in contracts:
        findings.extend(check_schema(contracts["delivery"], "delivery", "delivery", CONTRACT_PATHS["delivery"]))
        findings.extend(check_delivery(contracts["delivery"], root, CONTRACT_PATHS["delivery"], profile))
    if "compile_receipt" in contracts:
        findings.extend(check_schema(contracts["compile_receipt"], "compile_receipt", "delivery", CONTRACT_PATHS["compile_receipt"]))
        findings.extend(check_compile_receipt(contracts["compile_receipt"], root, CONTRACT_PATHS["compile_receipt"], contracts.get("paper_quality"), contracts.get("latex_template"), contracts.get("delivery"), profile))

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
                        gate_only=True,
                    )
                )

    findings.extend(check_decision_log(root, state))

    pending_review_count = sum(item.severity == "error" and item.gate_only for item in findings)
    automated_error_count = sum(item.severity == "error" and not item.gate_only for item in findings)
    blocking_error_count = automated_error_count + (pending_review_count if gate_mode == "enforce" else 0)
    if automated_error_count:
        gate_status = "blocked"
    elif pending_review_count:
        gate_status = "awaiting_review"
    else:
        gate_status = "passed"

    summary = {
        "project_ids": sorted(project_ids),
        "stage": stage,
        "profile": profile,
        "workflow_version": workflow_version,
        "gate_mode": gate_mode,
        "gate_status": gate_status,
        "pending_review_count": pending_review_count,
        "blocking_error_count": blocking_error_count,
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
