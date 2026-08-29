from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "cumcm-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from workflow_checks import check_project  # noqa: E402


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def review(decision: str = "accepted") -> dict:
    return {
        "decision": decision,
        "reviewer": "fixture-reviewer" if decision != "unreviewed" else None,
        "reviewed_at": "2026-08-30T12:00:00Z" if decision != "unreviewed" else None,
        "scope": "fixture",
        "notes": None,
    }


def envelope(kind: str) -> dict:
    return {
        "schema_version": "0.2.0",
        "artifact_type": kind,
        "project_id": "SYNTHETIC-2024-B",
        "updated_at": "2026-08-30T12:00:00Z",
        "producer": {"kind": "script", "name": "test-fixture", "version": "0.2.0"},
        "review": review(),
    }


def write_json(root: Path, rel: str, data: dict) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_valid_project(root: Path) -> None:
    source_bytes = b"synthetic problem statement"
    source_path = root / "problem" / "official" / "problem.txt"
    source_path.parent.mkdir(parents=True)
    source_path.write_bytes(source_bytes)

    code_path = root / "code" / "solve.py"
    code_path.parent.mkdir()
    code_path.write_text("print('synthetic')\n", encoding="utf-8")

    output = {"restricted_policy_cost": 12.5}
    output_bytes = (json.dumps(output) + "\n").encode()
    output_path = root / "runs" / "RUN-Q1-001" / "outputs" / "result.json"
    output_path.parent.mkdir(parents=True)
    output_path.write_bytes(output_bytes)
    stdout_path = root / "runs" / "RUN-Q1-001" / "stdout.log"
    stderr_path = root / "runs" / "RUN-Q1-001" / "stderr.log"
    stdout_path.write_text("synthetic run complete\n", encoding="utf-8")
    stderr_path.write_text("", encoding="utf-8")

    figure_bytes = b"synthetic figure bytes"
    figure_path = root / "figures" / "policy-cost.png"
    figure_path.parent.mkdir()
    figure_path.write_bytes(figure_bytes)

    paper_bytes = b"synthetic pdf bytes"
    paper_path = root / "paper" / "paper.pdf"
    paper_path.parent.mkdir()
    paper_path.write_bytes(paper_bytes)
    compile_log = root / "paper" / "compile.log"
    compile_log.write_text("compile succeeded\n", encoding="utf-8")

    state = envelope("workflow_state")
    state.update(
        {
            "workflow_version": "0.2.0",
            "current_stage": "delivery",
            "stages": {stage: "passed" for stage in (
                "intake",
                "problem-analysis",
                "model-design",
                "computation",
                "validation",
                "paper",
                "delivery",
            )},
        }
    )
    write_json(root, ".cumcm/state.json", state)

    sources = envelope("source_manifest")
    sources["sources"] = [
        {
            "source_id": "SRC-001",
            "path": "problem/official/problem.txt",
            "sha256": digest(source_bytes),
            "size": len(source_bytes),
            "media_type": "text/plain",
            "origin": "official",
            "authoritative_for": ["FACT-Q1-001"],
            "derived_from": None,
            "mutable": False,
        }
    ]
    write_json(root, "problem/SOURCE_MANIFEST.json", sources)

    facts = envelope("problem_facts")
    facts.update(
        {
            "subproblems": [
                {
                    "subproblem_id": "Q1",
                    "request": "Optimize within a declared fixed policy class.",
                    "expected_output": "Restricted-class minimum cost",
                }
            ],
            "facts": [
                {
                    "fact_id": "FACT-Q1-001",
                    "statement": "The fixture uses a synthetic fixed policy class.",
                    "source_id": "SRC-001",
                    "location": "line 1",
                    "raw_value": "fixed",
                    "normalized_value": "fixed",
                    "unit": None,
                    "extraction_method": "native_text",
                    "render_verified": True,
                }
            ],
            "definitions": [],
            "ambiguities": [],
            "assumptions": [],
        }
    )
    write_json(root, "analysis/PROBLEM_FACTS.json", facts)

    capabilities = envelope("task_capabilities")
    capabilities["capabilities"] = [
        {
            "capability_id": "CAP-Q1-001",
            "subproblem_id": "Q1",
            "objective": "Enumerate the fixed policy class.",
            "required_output": "Minimum cost in that class",
            "fact_ids": ["FACT-Q1-001"],
            "acceptance_checks": [{"type": "enumeration_coverage", "expected": "all fixed policies"}],
            "model_ids": ["MODEL-Q1-001"],
            "code_entry_points": ["code/solve.py:main"],
            "result_ids": ["RES-Q1-001"],
            "lifecycle_state": "validated",
            "blocking_issues": [],
        }
    ]
    write_json(root, "analysis/TASK_CAPABILITIES.json", capabilities)

    model = envelope("model_contract")
    model["components"] = [
        {
            "model_id": "MODEL-Q1-001",
            "capability_ids": ["CAP-Q1-001"],
            "variables": [{"name": "policy", "domain": "finite fixed class"}],
            "inputs": ["SRC-001"],
            "outputs": ["RES-Q1-001"],
            "method": "complete enumeration",
            "scope": "fixed homogeneous policies only; excludes feedback policies",
            "verification_plan": ["compare enumerated count with class cardinality"],
            "alternatives_considered": ["feedback-policy dynamic program"],
            "strong_claims": [],
        }
    ]
    write_json(root, "model/MODEL_CONTRACT.json", model)

    cross = envelope("cross_question_ledger")
    cross["shared_items"] = []
    write_json(root, "model/CROSS_QUESTION_LEDGER.json", cross)

    run = envelope("run_manifest")
    run.update(
        {
            "run_id": "RUN-Q1-001",
            "purpose": "synthetic restricted-policy regression",
            "subproblem_id": "Q1",
            "capability_ids": ["CAP-Q1-001"],
            "argv": ["python3", "code/solve.py"],
            "working_directory": ".",
            "started_at": "2026-08-30T12:00:00Z",
            "finished_at": "2026-08-30T12:00:01Z",
            "exit_code": 0,
            "status": "completed",
            "inputs": [
                {
                    "path": "problem/official/problem.txt",
                    "evidence_role": "formal_input",
                    "sha256": digest(source_bytes),
                    "size": len(source_bytes),
                    "media_type": "text/plain",
                }
            ],
            "outputs": [
                {
                    "path": "runs/RUN-Q1-001/outputs/result.json",
                    "evidence_role": "claim_bearing_output",
                    "sha256": digest(output_bytes),
                    "size": len(output_bytes),
                    "media_type": "application/json",
                }
            ],
            "environment": {"python": "3.x", "platform": "synthetic"},
            "stdout_path": "runs/RUN-Q1-001/stdout.log",
            "stderr_path": "runs/RUN-Q1-001/stderr.log",
            "assertions": [{"name": "enumeration coverage", "passed": True}],
            "parent_run_id": None,
        }
    )
    write_json(root, "runs/RUN-Q1-001/RUN_MANIFEST.json", run)

    results = envelope("results_index")
    results["results"] = [
        {
            "result_id": "RES-Q1-001",
            "name": "Restricted policy minimum cost",
            "value": 12.5,
            "unit": "synthetic_cost",
            "precision": 0.1,
            "display_rounding": 1,
            "run_id": "RUN-Q1-001",
            "output_locator": "runs/RUN-Q1-001/outputs/result.json#/restricted_policy_cost",
            "scope": "fixed homogeneous policies only",
            "evidence_state": "supported_not_reproduced",
            "validation_checks": ["enumeration coverage"],
            "supersedes": None,
        }
    ]
    write_json(root, "results/RESULTS_INDEX.json", results)

    figures = envelope("figure_manifest")
    figures["figures"] = [
        {
            "figure_id": "FIG-Q1-001",
            "kind": "quantitative",
            "purpose": "Show the restricted-class comparison.",
            "path": "figures/policy-cost.png",
            "sha256": digest(figure_bytes),
            "result_ids": ["RES-Q1-001"],
            "run_ids": ["RUN-Q1-001"],
            "axes": [{"name": "policy", "unit": "category"}],
            "transformations": [],
            "caption_claims": ["Restricted-class comparison only."],
            "paper_location": "Results",
            "visual_review": review(),
        }
    ]
    write_json(root, "figures/FIGURE_MANIFEST.json", figures)

    claims = envelope("claim_ledger")
    claims.update(
        {
            "independent_review": review(),
            "claims": [
                {
                    "claim_id": "CLM-Q1-001",
                    "text": "The reported policy minimizes cost within the enumerated fixed homogeneous policy class.",
                    "claim_type": "scoped_optimality",
                    "scope": "fixed homogeneous policies only; excludes feedback policies",
                    "paper_location": "Results",
                    "evidence": {
                        "fact_ids": ["FACT-Q1-001"],
                        "model_ids": ["MODEL-Q1-001"],
                        "run_ids": ["RUN-Q1-001"],
                        "result_ids": ["RES-Q1-001"],
                        "figure_ids": ["FIG-Q1-001"],
                    },
                    "evidence_state": "supported_not_reproduced",
                    "certificates": [],
                    "review": review(),
                }
            ],
        }
    )
    write_json(root, "validation/CLAIM_LEDGER.json", claims)

    delivery = envelope("delivery_manifest")
    delivery.update(
        {
            "profile": "strict",
            "files": [
                {
                    "path": "paper/paper.pdf",
                    "role": "submission_pdf",
                    "sha256": digest(paper_bytes),
                    "size": len(paper_bytes),
                }
            ],
            "compile": {
                "command": "xelatex paper.tex",
                "engine": "XeLaTeX",
                "exit_code": 0,
                "log_path": "paper/compile.log",
                "warnings": [],
                "page_count": 1,
            },
            "unresolved_errors": [],
            "accepted_exceptions": [],
            "excluded_files": [],
            "final_review": review(),
        }
    )
    write_json(root, "delivery/DELIVERY_MANIFEST.json", delivery)


class V02WorkflowTests(unittest.TestCase):
    def run_check(self, root: Path, profile: str = "strict"):
        findings, summary = check_project(root, "delivery", profile)
        return findings, summary

    def test_complete_project_passes_without_errors(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            findings, summary = self.run_check(root)
            self.assertEqual([f for f in findings if f.severity == "error"], [])
            self.assertEqual(summary["run_count"], 1)

    def test_all_json_schemas_are_valid_draft_2020_12(self):
        schema_dir = ROOT / ".agents" / "skills" / "cumcm-workflow" / "schemas"
        schemas = sorted(schema_dir.glob("*.schema.json"))
        self.assertEqual(len(schemas), 12)
        for path in schemas:
            with self.subTest(schema=path.name):
                Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))

    def test_dispatcher_writes_machine_readable_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "cumcm_check.py"),
                    "--project",
                    str(root),
                    "--all",
                    "--profile",
                    "strict",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            report = json.loads((root / ".cumcm" / "validation-report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["summary"]["finding_counts"]["error"], 0)
            self.assertIn("does not prove mathematical correctness", report["summary"]["evidence_boundary"])

    def test_source_hash_change_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            (root / "problem" / "official" / "problem.txt").write_text("changed", encoding="utf-8")
            findings, _ = self.run_check(root)
            self.assertIn("SOURCE-E008", {item.rule_id for item in findings})

    def test_source_size_mismatch_is_warning_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "problem" / "SOURCE_MANIFEST.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["sources"][0]["size"] += 1
            write_json(root, "problem/SOURCE_MANIFEST.json", data)
            findings, _ = self.run_check(root)
            finding_by_rule = {item.rule_id: item for item in findings}
            self.assertEqual(finding_by_rule["SOURCE-W009"].severity, "warning")
            self.assertEqual([item for item in findings if item.severity == "error"], [])

    def test_fact_cannot_cite_an_unknown_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "analysis" / "PROBLEM_FACTS.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["facts"][0]["source_id"] = "SRC-UNKNOWN"
            write_json(root, "analysis/PROBLEM_FACTS.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("FACT-E006", {item.rule_id for item in findings})

    def test_implemented_capability_code_entry_must_exist(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "analysis" / "TASK_CAPABILITIES.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["capabilities"][0]["code_entry_points"] = ["code/missing.py:main"]
            write_json(root, "analysis/TASK_CAPABILITIES.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("CAP-E011", {item.rule_id for item in findings})

    def test_run_output_hash_must_match(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "runs" / "RUN-Q1-001" / "RUN_MANIFEST.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["outputs"][0]["sha256"] = "0" * 64
            write_json(root, "runs/RUN-Q1-001/RUN_MANIFEST.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("RUN-E007", {item.rule_id for item in findings})

    def test_run_size_mismatch_is_warning_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "runs" / "RUN-Q1-001" / "RUN_MANIFEST.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["outputs"][0]["size"] += 1
            write_json(root, "runs/RUN-Q1-001/RUN_MANIFEST.json", data)
            findings, _ = self.run_check(root)
            finding_by_rule = {item.rule_id: item for item in findings}
            self.assertEqual(finding_by_rule["RUN-W013"].severity, "warning")
            self.assertEqual([item for item in findings if item.severity == "error"], [])

    def test_auxiliary_input_and_intermediate_output_may_omit_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            auxiliary = root / "runs" / "RUN-Q1-001" / "notes.txt"
            intermediate = root / "runs" / "RUN-Q1-001" / "outputs" / "preview.txt"
            auxiliary.write_text("non-result-affecting note\n", encoding="utf-8")
            intermediate.write_text("presentation preview\n", encoding="utf-8")
            path = root / "runs" / "RUN-Q1-001" / "RUN_MANIFEST.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["inputs"].append(
                {
                    "path": "runs/RUN-Q1-001/notes.txt",
                    "evidence_role": "auxiliary_input",
                    "size": auxiliary.stat().st_size,
                    "media_type": "text/plain",
                }
            )
            data["outputs"].append(
                {
                    "path": "runs/RUN-Q1-001/outputs/preview.txt",
                    "evidence_role": "intermediate_output",
                    "size": intermediate.stat().st_size,
                    "media_type": "text/plain",
                }
            )
            write_json(root, "runs/RUN-Q1-001/RUN_MANIFEST.json", data)
            findings, _ = self.run_check(root)
            self.assertEqual([item for item in findings if item.severity == "error"], [])

    def test_legacy_v02_run_records_without_roles_remain_strict(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "runs" / "RUN-Q1-001" / "RUN_MANIFEST.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["inputs"][0].pop("evidence_role")
            data["outputs"][0].pop("evidence_role")
            write_json(root, "runs/RUN-Q1-001/RUN_MANIFEST.json", data)
            findings, _ = self.run_check(root)
            self.assertEqual([item for item in findings if item.severity == "error"], [])

            data["outputs"][0].pop("sha256")
            write_json(root, "runs/RUN-Q1-001/RUN_MANIFEST.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("RUN-E015", {item.rule_id for item in findings})

    def test_indexed_result_must_use_claim_bearing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "runs" / "RUN-Q1-001" / "RUN_MANIFEST.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["outputs"][0]["evidence_role"] = "intermediate_output"
            data["outputs"][0].pop("sha256")
            write_json(root, "runs/RUN-Q1-001/RUN_MANIFEST.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("RESULT-E015", {item.rule_id for item in findings})

    def test_stale_optional_hash_is_warning_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            intermediate = root / "runs" / "RUN-Q1-001" / "outputs" / "preview.txt"
            intermediate.write_text("presentation preview\n", encoding="utf-8")
            path = root / "runs" / "RUN-Q1-001" / "RUN_MANIFEST.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["outputs"].append(
                {
                    "path": "runs/RUN-Q1-001/outputs/preview.txt",
                    "evidence_role": "intermediate_output",
                    "sha256": "0" * 64,
                    "size": intermediate.stat().st_size,
                    "media_type": "text/plain",
                }
            )
            write_json(root, "runs/RUN-Q1-001/RUN_MANIFEST.json", data)
            findings, _ = self.run_check(root)
            finding_by_rule = {item.rule_id: item for item in findings}
            self.assertEqual(finding_by_rule["RUN-W007"].severity, "warning")
            self.assertEqual([item for item in findings if item.severity == "error"], [])

    def test_figure_hash_drift_is_warning_during_paper_editing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            (root / "figures" / "policy-cost.png").write_bytes(b"edited figure bytes")
            findings, _ = check_project(root, "paper", "strict")
            finding_by_rule = {item.rule_id: item for item in findings}
            self.assertEqual(finding_by_rule["FIGURE-W011"].severity, "warning")
            self.assertEqual([item for item in findings if item.severity == "error"], [])

    def test_figure_cannot_use_unindexed_result(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "figures" / "FIGURE_MANIFEST.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["figures"][0]["result_ids"] = ["RES-UNKNOWN"]
            write_json(root, "figures/FIGURE_MANIFEST.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("FIGURE-E006", {item.rule_id for item in findings})

    def test_global_overclaim_requires_certificate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "validation" / "CLAIM_LEDGER.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["claims"][0]["text"] = "This is the globally optimal policy."
            write_json(root, "validation/CLAIM_LEDGER.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("CLAIM-E011", {item.rule_id for item in findings})

    def test_certificate_declaration_requires_real_evidence_ids(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "validation" / "CLAIM_LEDGER.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["claims"][0]["text"] = "This is the globally optimal policy."
            data["claims"][0]["certificates"] = [
                {
                    "type": "global_optimality",
                    "description": "Synthetic certificate declaration",
                    "evidence_ids": ["UNKNOWN-EVIDENCE"],
                    "scope": "all feedback policies",
                }
            ]
            write_json(root, "validation/CLAIM_LEDGER.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("CLAIM-E017", {item.rule_id for item in findings})

    def test_robustness_claim_requires_a_validation_method(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "validation" / "CLAIM_LEDGER.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["claims"][0]["text"] = "The result is robust."
            data["claims"][0]["certificates"] = [
                {
                    "type": "robustness",
                    "description": "Declared without a sensitivity method",
                    "evidence_ids": ["RES-Q1-001"],
                    "scope": "synthetic fixture",
                }
            ]
            write_json(root, "validation/CLAIM_LEDGER.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("CLAIM-E019", {item.rule_id for item in findings})

    def test_validated_capability_requires_an_execution_run(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "analysis" / "TASK_CAPABILITIES.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["capabilities"].append(
                {
                    "capability_id": "CAP-Q1-002",
                    "subproblem_id": "Q1",
                    "objective": "Second declared computation",
                    "required_output": "Second result",
                    "fact_ids": ["FACT-Q1-001"],
                    "acceptance_checks": [{"type": "synthetic"}],
                    "model_ids": ["MODEL-Q1-001"],
                    "code_entry_points": ["code/solve.py:main"],
                    "result_ids": [],
                    "lifecycle_state": "validated",
                    "blocking_issues": [],
                }
            )
            write_json(root, "analysis/TASK_CAPABILITIES.json", data)
            model_path = root / "model" / "MODEL_CONTRACT.json"
            model = json.loads(model_path.read_text(encoding="utf-8"))
            model["components"][0]["capability_ids"].append("CAP-Q1-002")
            write_json(root, "model/MODEL_CONTRACT.json", model)
            findings, _ = self.run_check(root)
            self.assertIn("RUN-E014", {item.rule_id for item in findings})

    def test_full_project_can_be_checked_through_every_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            for stage in (
                "intake",
                "problem-analysis",
                "model-design",
                "computation",
                "validation",
                "paper",
                "delivery",
            ):
                with self.subTest(stage=stage):
                    findings, _ = check_project(root, stage, "strict")
                    self.assertEqual([item for item in findings if item.severity == "error"], [])

    def test_sprint_does_not_demote_execution_hash_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            delivery_path = root / "delivery" / "DELIVERY_MANIFEST.json"
            delivery = json.loads(delivery_path.read_text(encoding="utf-8"))
            delivery["profile"] = "sprint"
            delivery["files"][0]["sha256"] = "0" * 64
            write_json(root, "delivery/DELIVERY_MANIFEST.json", delivery)
            findings, _ = self.run_check(root, profile="sprint")
            finding_by_rule = {item.rule_id: item for item in findings}
            self.assertEqual(finding_by_rule["DELIVERY-E007"].severity, "error")

    def test_final_figure_hash_is_hard_when_frozen_for_delivery(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            delivery_path = root / "delivery" / "DELIVERY_MANIFEST.json"
            delivery = json.loads(delivery_path.read_text(encoding="utf-8"))
            figure_path = root / "figures" / "policy-cost.png"
            delivery["files"].append(
                {
                    "path": "figures/policy-cost.png",
                    "role": "final_figure",
                    "sha256": "0" * 64,
                    "size": figure_path.stat().st_size,
                }
            )
            write_json(root, "delivery/DELIVERY_MANIFEST.json", delivery)
            findings, _ = self.run_check(root)
            finding_by_rule = {item.rule_id: item for item in findings}
            self.assertEqual(finding_by_rule["DELIVERY-E007"].severity, "error")

    def test_delivery_size_mismatch_is_warning_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            delivery_path = root / "delivery" / "DELIVERY_MANIFEST.json"
            delivery = json.loads(delivery_path.read_text(encoding="utf-8"))
            delivery["files"][0]["size"] += 1
            write_json(root, "delivery/DELIVERY_MANIFEST.json", delivery)
            findings, _ = self.run_check(root)
            finding_by_rule = {item.rule_id: item for item in findings}
            self.assertEqual(finding_by_rule["DELIVERY-W008"].severity, "warning")
            self.assertEqual([item for item in findings if item.severity == "error"], [])

    def test_cross_question_unit_conflict_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "model" / "CROSS_QUESTION_LEDGER.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["shared_items"] = [
                {
                    "shared_id": "SHARED-001",
                    "name": "time",
                    "producer": "Q1",
                    "consumers": ["Q1"],
                    "definition": "elapsed time",
                    "unit": "s",
                    "transformation": None,
                    "uncertainty_propagation": None,
                    "authoritative_artifact": "RES-Q1-001",
                    "conflict_status": "clear",
                },
                {
                    "shared_id": "SHARED-002",
                    "name": "time",
                    "producer": "Q1",
                    "consumers": ["Q1"],
                    "definition": "elapsed time",
                    "unit": "day",
                    "transformation": None,
                    "uncertainty_propagation": None,
                    "authoritative_artifact": "RES-Q1-001",
                    "conflict_status": "unresolved",
                },
            ]
            write_json(root, "model/CROSS_QUESTION_LEDGER.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("CROSS-E007", {item.rule_id for item in findings})

    def test_indexed_value_must_match_executed_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "results" / "RESULTS_INDEX.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["results"][0]["value"] = 99.0
            write_json(root, "results/RESULTS_INDEX.json", data)
            findings, _ = self.run_check(root)
            self.assertIn("RESULT-E012", {item.rule_id for item in findings})


if __name__ == "__main__":
    unittest.main()
