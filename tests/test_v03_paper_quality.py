from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "cumcm-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from test_workflow_core import build_valid_project, envelope, review, write_json  # noqa: E402
from init_latex_paper import initialize as initialize_latex  # noqa: E402
from workflow_checks import check_project  # noqa: E402


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record_decisions(root: Path, stages: tuple[str, ...]) -> None:
    for index, stage in enumerate(stages, 1):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "record_decision.py"),
                "--project",
                str(root),
                "--stage",
                stage,
                "--decision",
                "accepted",
                "--decision-id",
                f"DEC-{index:03d}",
                "--reviewer",
                "fixture-reviewer",
                "--task-turn-ref",
                f"fixture-turn-{index}",
                "--summary",
                f"Accepted fixture stage {stage}",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode:
            raise AssertionError(completed.stdout + completed.stderr)


def build_valid_v03_project(root: Path, *, decisions: tuple[str, ...] | None = None) -> None:
    build_valid_project(root)
    paper_path = root / "paper" / "paper.pdf"
    paper_artifact = {"path": "paper/paper.pdf", "sha256": digest_file(paper_path)}

    included_layer = {
        "status": "included",
        "summary": "The paper records this part of the argument chain.",
        "evidence_ids": ["CLM-Q1-001"],
        "rationale": None,
    }
    plan = envelope("paper_plan")
    plan.update(
        {
            "reference_reviews": [
                {
                    "reference_id": "REF-001",
                    "source": "reviewed high-quality contest paper",
                    "quality_reasons": ["complete derivation and verification chain"],
                    "transferable_lessons": ["connect each conclusion to evidence"],
                    "non_transferable_limits": ["different problem and data"],
                }
            ],
            "claims_evidence_matrix": [
                {
                    "claim_id": "CLM-Q1-001",
                    "subproblem_id": "Q1",
                    "planned_sections": ["Results"],
                    "evidence_ids": ["RES-Q1-001", "FIG-Q1-001"],
                    "status": "included",
                }
            ],
            "question_argument_chains": [
                {
                    "subproblem_id": "Q1",
                    "layers": {
                        name: dict(included_layer)
                        for name in (
                            "problem_interpretation",
                            "assumptions_boundaries",
                            "variables_parameters",
                            "objective_constraints",
                            "derivation",
                            "algorithm",
                            "results",
                            "validation",
                            "limitations",
                        )
                    },
                }
            ],
            "figure_plan": [
                {
                    "figure_id": "FIG-Q1-001",
                    "kind": "quantitative",
                    "purpose": "Explain the restricted-policy comparison.",
                    "claim_ids": ["CLM-Q1-001"],
                    "result_ids": ["RES-Q1-001"],
                    "required": True,
                    "decision_support": "Makes the policy comparison inspectable.",
                }
            ],
            "page_budget": [
                {"section": "Q1", "purpose": "Complete argument", "target_pages": 1.0}
            ],
        }
    )
    write_json(root, "paper/PAPER_PLAN.json", plan)

    initialize_latex(root, "Synthetic CUMCM Paper", 2026, "synthetic; evidence")
    for source in (root / "paper").rglob("*.tex"):
        text = source.read_text(encoding="utf-8")
        text = text.replace("CUMCM-TODO", "已完成").replace("\\placeholder{", "\\textbf{")
        source.write_text(text, encoding="utf-8")
    manifest_path = root / "paper" / "LATEX_TEMPLATE_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["official_compliance"] = "verified_against_current_rules"
    manifest["official_template_source"] = "fixture://current-rules"
    manifest["review"] = review()
    write_json(root, "paper/LATEX_TEMPLATE_MANIFEST.json", manifest)

    dimension = {"status": "pass", "notes": "Checked against linked evidence.", "evidence_ids": ["CLM-Q1-001"]}
    quality = envelope("paper_quality_report")
    quality.update(
        {
            "paper_status": "final",
            "paper_artifact": paper_artifact,
            "content_review": {
                "decision": "accepted",
                "reviewer": "fixture-reviewer",
                "reviewed_at": "2026-08-30T12:00:00Z",
                "artifact": paper_artifact,
                "questions": [
                    {
                        "subproblem_id": "Q1",
                        "argument_chain": dict(dimension),
                        "derivation": dict(dimension),
                        "result_interpretation": dict(dimension),
                        "validation_strength": dict(dimension),
                        "limitations": dict(dimension),
                    }
                ],
            },
            "layout_review": {
                "decision": "accepted",
                "reviewer": "fixture-reviewer",
                "reviewed_at": "2026-08-30T12:00:00Z",
                "artifact": paper_artifact,
                "page_count": 1,
                "rendered_pages": [1],
                "checks": [
                    {"check_id": "LAYOUT-001", "category": "cross_page", "status": "pass", "notes": "All rendered pages inspected."}
                ],
            },
            "final_qa": {
                "decision": "accepted",
                "reviewer": "fixture-reviewer",
                "reviewed_at": "2026-08-30T12:00:00Z",
                "artifact": paper_artifact,
                "notes": "Final bytes match the reviewed artifact.",
            },
            "open_issues": [],
        }
    )
    write_json(root, "paper/PAPER_QUALITY_REPORT.json", quality)

    revisions = envelope("paper_revision_log")
    revisions.update({"initial_snapshot": paper_artifact, "revisions": []})
    write_json(root, "paper/PAPER_REVISION_LOG.json", revisions)

    receipt = envelope("compile_receipt")
    receipt.update(
        {
            "selected_attempt_id": "COMPILE-001",
            "attempts": [
                {
                    "attempt_id": "COMPILE-001",
                    "argv": ["xelatex", "paper.tex"],
                    "engine": "XeLaTeX",
                    "engine_version": "synthetic",
                    "exit_code": 0,
                    "log_path": "paper/compile.log",
                    "warnings": [],
                    "page_count": 1,
                    "pdf_path": "paper/paper.pdf",
                    "pdf_sha256": paper_artifact["sha256"],
                    "font_check": "pass",
                    "glyph_check": "pass",
                    "diagnostic_summary": "Synthetic compile succeeded.",
                    "completed_at": "2026-08-30T12:00:00Z",
                }
            ],
            "layout_review_binding": {
                "quality_report_path": "paper/PAPER_QUALITY_REPORT.json",
                "quality_report_sha256": digest_file(root / "paper" / "PAPER_QUALITY_REPORT.json"),
                "pdf_sha256": paper_artifact["sha256"],
            },
        }
    )
    write_json(root, "delivery/COMPILE_RECEIPT.json", receipt)
    delivery_path = root / "delivery" / "DELIVERY_MANIFEST.json"
    delivery = json.loads(delivery_path.read_text(encoding="utf-8"))
    delivery["compile_receipt_path"] = "delivery/COMPILE_RECEIPT.json"
    write_json(root, "delivery/DELIVERY_MANIFEST.json", delivery)

    state_path = root / ".cumcm" / "state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["current_stage"] = "delivery"
    state["stages"] = {stage: "passed" for stage in (
        "intake", "problem-analysis", "model-design", "computation", "validation", "paper", "delivery"
    )}
    write_json(root, ".cumcm/state.json", state)

    record_decisions(
        root,
        decisions
        if decisions is not None
        else ("intake", "problem-analysis", "model-design", "computation", "validation", "paper", "delivery"),
    )


def set_state(root: Path, current: str, paper_status: str, delivery_status: str) -> None:
    path = root / ".cumcm" / "state.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["current_stage"] = current
    data["stages"]["paper"] = paper_status
    data["stages"]["delivery"] = delivery_status
    write_json(root, ".cumcm/state.json", data)


class V03PaperQualityTests(unittest.TestCase):
    def test_complete_v03_project_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            findings, summary = check_project(root, "delivery", "strict")
            self.assertEqual([item for item in findings if item.severity == "error"], [])
            self.assertEqual(summary["workflow_version"], "0.3.0")
            self.assertEqual(summary["gate_status"], "passed")

    def test_missing_argument_layer_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "PAPER_PLAN.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            del data["question_argument_chains"][0]["layers"]["derivation"]
            write_json(root, "paper/PAPER_PLAN.json", data)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("PPLAN-E008", {item.rule_id for item in findings})

    def test_not_applicable_layer_requires_rationale(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "PAPER_PLAN.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            layer = data["question_argument_chains"][0]["layers"]["derivation"]
            layer.update({"status": "not_applicable", "rationale": None, "evidence_ids": []})
            write_json(root, "paper/PAPER_PLAN.json", data)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("PPLAN-E010", {item.rule_id for item in findings})

    def test_required_planned_figure_must_exist(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "PAPER_PLAN.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["figure_plan"].append(
                {
                    "figure_id": "FIG-Q1-999",
                    "kind": "quantitative",
                    "purpose": "Required sensitivity view.",
                    "claim_ids": ["CLM-Q1-001"],
                    "result_ids": ["RES-Q1-001"],
                    "required": True,
                    "decision_support": "Tests decision sensitivity.",
                }
            )
            write_json(root, "paper/PAPER_PLAN.json", data)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("PPLAN-E012", {item.rule_id for item in findings})

    def test_quantitative_figure_plan_needs_claim_and_result_role(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "PAPER_PLAN.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["figure_plan"][0]["claim_ids"] = []
            write_json(root, "paper/PAPER_PLAN.json", data)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("PPLAN-E015", {item.rule_id for item in findings})

    def test_review_only_failure_is_preflight_zero_and_enforce_nonzero(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root, decisions=("intake", "problem-analysis", "model-design", "computation", "validation"))
            set_state(root, "paper", "awaiting_review", "not_started")
            path = root / "paper" / "PAPER_QUALITY_REPORT.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["content_review"]["decision"] = "unreviewed"
            write_json(root, "paper/PAPER_QUALITY_REPORT.json", data)
            preflight_findings, preflight = check_project(root, "paper", "strict", "preflight")
            _, enforce = check_project(root, "paper", "strict", "enforce")
            self.assertIn("PQUALITY-E010", {item.rule_id for item in preflight_findings})
            self.assertEqual(preflight["blocking_error_count"], 0)
            self.assertEqual(preflight["gate_status"], "awaiting_review")
            self.assertGreater(enforce["blocking_error_count"], 0)
            preflight_cli = subprocess.run(
                [sys.executable, str(SCRIPTS / "cumcm_check.py"), "--project", str(root), "--stage", "paper", "--profile", "strict", "--gate-mode", "preflight", "--no-write-report"],
                check=False,
                capture_output=True,
                text=True,
            )
            enforce_cli = subprocess.run(
                [sys.executable, str(SCRIPTS / "cumcm_check.py"), "--project", str(root), "--stage", "paper", "--profile", "strict", "--gate-mode", "enforce", "--no-write-report"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(preflight_cli.returncode, 0, preflight_cli.stdout + preflight_cli.stderr)
            self.assertEqual(enforce_cli.returncode, 1)

    def test_strict_layout_review_must_cover_all_pages(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "PAPER_QUALITY_REPORT.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["layout_review"]["page_count"] = 2
            write_json(root, "paper/PAPER_QUALITY_REPORT.json", data)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("PQUALITY-E008", {item.rule_id for item in findings})

    def test_final_paper_cannot_have_open_p0_issue(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "PAPER_QUALITY_REPORT.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["open_issues"] = [{"issue_id": "ISSUE-001", "severity": "P0", "category": "content", "status": "open", "description": "Missing derivation", "location": "Q1", "resolution": None, "verified_by": None}]
            write_json(root, "paper/PAPER_QUALITY_REPORT.json", data)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("PQUALITY-E011", {item.rule_id for item in findings})

    def test_revision_snapshot_hash_drift_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "PAPER_REVISION_LOG.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["initial_snapshot"]["sha256"] = "0" * 64
            write_json(root, "paper/PAPER_REVISION_LOG.json", data)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("PREVISION-E003", {item.rule_id for item in findings})

    def test_closed_issue_requires_verified_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "PAPER_QUALITY_REPORT.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["open_issues"] = [{"issue_id": "ISSUE-001", "severity": "P1", "category": "content", "status": "closed", "description": "Clarify result scope", "location": "Q1", "resolution": "Edited prose", "verified_by": "fixture-reviewer"}]
            write_json(root, "paper/PAPER_QUALITY_REPORT.json", data)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("PREVISION-E005", {item.rule_id for item in findings})

    def test_compile_receipt_page_count_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "delivery" / "COMPILE_RECEIPT.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["attempts"][0]["page_count"] = 2
            write_json(root, "delivery/COMPILE_RECEIPT.json", data)
            findings, _ = check_project(root, "delivery", "strict")
            self.assertIn("COMPILE-E010", {item.rule_id for item in findings})

    def test_decision_hash_chain_tampering_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / ".cumcm" / "decisions.jsonl"
            lines = path.read_text(encoding="utf-8").splitlines()
            event = json.loads(lines[0])
            event["user_visible_summary"] = "tampered"
            lines[0] = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            findings, _ = check_project(root, "delivery", "strict")
            self.assertIn("DECISION-E006", {item.rule_id for item in findings})

    def test_stale_decision_scope_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "PAPER_PLAN.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["updated_at"] = "2026-08-30T13:00:00Z"
            write_json(root, "paper/PAPER_PLAN.json", data)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("DECISION-E010", {item.rule_id for item in findings})

    def test_record_decision_rejects_duplicate_id(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "record_decision.py"),
                    "--project",
                    str(root),
                    "--stage",
                    "delivery",
                    "--decision",
                    "accepted",
                    "--decision-id",
                    "DEC-007",
                    "--reviewer",
                    "fixture-reviewer",
                    "--task-turn-ref",
                    "duplicate-test",
                    "--summary",
                    "Must not append.",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("already exists", completed.stderr)

    def test_missing_stage_decision_is_review_only_in_preflight(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root, decisions=("intake", "problem-analysis", "model-design", "computation", "validation"))
            set_state(root, "paper", "passed", "not_started")
            findings, summary = check_project(root, "paper", "strict", "preflight")
            self.assertIn("DECISION-E008", {item.rule_id for item in findings})
            self.assertEqual(summary["gate_status"], "awaiting_review")
            self.assertEqual(summary["blocking_error_count"], 0)

    def test_skill_and_docs_use_python3_entrypoint(self):
        targets = [
            ROOT / ".agents" / "skills" / "cumcm-workflow" / "SKILL.md",
            ROOT / "README.md",
        ]
        for path in targets:
            self.assertNotIn("python scripts/cumcm_check.py", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
