from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "cumcm-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend_selection import select_backend
from build_independent_review_package import build as build_review_package
from init_latex_paper import commit_staged_tree
from migrate_v04_to_v05 import migrate
from paper_visible_text_check import inspect_text
from test_v03_paper_quality import build_valid_v04_project
from test_workflow_core import build_valid_project, write_json
from workflow_checks import check_project, plan_scoped_revalidation


def review_finding(finding_id: str, severity: str, status: str) -> dict:
    return {
        "finding_id": finding_id,
        "severity": severity,
        "status": status,
        "category": "implementation",
        "location": "code/solve.py",
        "evidence": "fixture evidence",
        "recommendation": "fixture recommendation",
    }


class ContestNativeV05Tests(unittest.TestCase):
    def test_enforce_cannot_bypass_stage_state_or_decisions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            state_path = root / ".cumcm" / "state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["mode"] = "finalizing"
            state["stages"]["validation"] = "in_progress"
            write_json(root, ".cumcm/state.json", state)
            findings, summary = check_project(root, "validation", "strict", "enforce")
            rules = {item.rule_id for item in findings}
            self.assertIn("STATE-E013", rules)
            self.assertIn("DECISION-E001", rules)
            self.assertGreater(summary["blocking_error_count"], 0)

    def test_working_is_lightweight_and_finalizing_raises_formal_gates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            _, working = check_project(root, "validation", "strict", "enforce")
            self.assertEqual(working["gate_status"], "working_ready")
            self.assertEqual(working["blocking_error_count"], 0)
            state = json.loads((root / ".cumcm/state.json").read_text(encoding="utf-8"))
            state["mode"] = "finalizing"
            write_json(root, ".cumcm/state.json", state)
            findings, finalizing = check_project(root, "validation", "strict", "enforce")
            self.assertIn("PROJECT-E001", {item.rule_id for item in findings})
            self.assertGreater(finalizing["blocking_error_count"], 0)

    def test_accepted_with_concerns_and_p1_do_not_block_paper(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "validation" / "INDEPENDENT_REVIEW_RESULT.json"
            result = json.loads(path.read_text(encoding="utf-8"))
            result["verdict"] = "accepted_with_concerns"
            result["findings"] = [review_finding("REV-P1-001", "P1", "open")]
            write_json(root, "validation/INDEPENDENT_REVIEW_RESULT.json", result)
            findings, summary = check_project(root, "validation", "strict", "enforce")
            self.assertIn("IREVIEW-W001", {item.rule_id for item in findings})
            self.assertNotIn("IREVIEW-E012", {item.rule_id for item in findings})
            self.assertEqual(summary["blocking_error_count"], 0)

    def test_open_p0_is_the_only_review_severity_that_requires_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            path = root / "validation" / "INDEPENDENT_REVIEW_RESULT.json"
            result = json.loads(path.read_text(encoding="utf-8"))
            result["verdict"] = "revision_required"
            result["findings"] = [review_finding("REV-P0-001", "P0", "open")]
            write_json(root, "validation/INDEPENDENT_REVIEW_RESULT.json", result)
            findings, summary = check_project(root, "validation", "strict", "enforce")
            self.assertIn("IREVIEW-E012", {item.rule_id for item in findings})
            self.assertGreater(summary["blocking_error_count"], 0)

    def test_targeted_rereview_covers_prior_p0_without_new_full_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            current_path = root / "validation" / "INDEPENDENT_REVIEW_RESULT.json"
            prior = json.loads(current_path.read_text(encoding="utf-8"))
            prior["review_id"] = "REVIEW-FULL-001"
            prior["verdict"] = "revision_required"
            prior["findings"] = [review_finding("REV-P0-001", "P0", "open")]
            write_json(root, "validation/review-history/REVIEW-FULL-001.json", prior)

            package_path = root / "validation" / "independent-review-package" / "REVIEW_PACKAGE_MANIFEST.json"
            package = json.loads(package_path.read_text(encoding="utf-8"))
            package.update({"review_mode": "targeted", "previous_review_path": "validation/review-history/REVIEW-FULL-001.json", "target_finding_ids": ["REV-P0-001"]})
            write_json(root, "validation/independent-review-package/REVIEW_PACKAGE_MANIFEST.json", package)

            result = json.loads(current_path.read_text(encoding="utf-8"))
            result.update({
                "review_id": "REVIEW-TARGETED-002",
                "review_mode": "targeted",
                "previous_review_path": "validation/review-history/REVIEW-FULL-001.json",
                "target_finding_ids": ["REV-P0-001"],
                "verdict": "accepted",
                "findings": [review_finding("REV-P0-001", "P0", "resolved")],
            })
            write_json(root, "validation/INDEPENDENT_REVIEW_RESULT.json", result)
            findings, summary = check_project(root, "validation", "strict", "enforce")
            rules = {item.rule_id for item in findings}
            self.assertNotIn("IREVIEW-E024", rules)
            self.assertNotIn("IREVIEW-E012", rules)
            self.assertEqual(summary["blocking_error_count"], 0)

    def test_stage_snapshot_trust_ends_when_code_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v04_project(root)
            _, before = check_project(root, "delivery", "strict")
            self.assertIn("computation", before["trusted_snapshots"])
            (root / "code" / "solve.py").write_text("print('changed after official run')\n", encoding="utf-8")
            findings, after = check_project(root, "delivery", "strict")
            self.assertNotIn("computation", after["trusted_snapshots"])
            self.assertIn("RUN-E020", {item.rule_id for item in findings})

    def test_revision_requested_invalidates_stage_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v04_project(root)
            completed = __import__("subprocess").run(
                [sys.executable, str(SCRIPTS / "record_decision.py"), "--project", str(root),
                 "--stage", "computation", "--decision", "revision_requested",
                 "--decision-id", "DEC-COMP-REVISION", "--reviewer", "fixture-reviewer",
                 "--task-turn-ref", "revision-test", "--summary", "Computation needs revision."],
                check=False, capture_output=True, text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertFalse((root / ".cumcm/snapshots/computation.json").exists())
            _, summary = check_project(root, "delivery", "strict")
            self.assertNotIn("computation", summary["trusted_snapshots"])

    def test_finalizing_requires_derived_stage_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v04_project(root)
            (root / ".cumcm/snapshots/validation.json").unlink()
            findings, summary = check_project(root, "delivery", "strict")
            self.assertIn("DECISION-E014", {item.rule_id for item in findings})
            self.assertGreater(summary["blocking_error_count"], 0)

    def test_scoped_revalidation_does_not_default_to_full_workspace(self):
        local = plan_scoped_revalidation(["paper/sections/q1.tex"], "local", "delivery")
        semantic = plan_scoped_revalidation(["model/MODEL_CONTRACT.json"], "semantic", "delivery")
        cosmetic = plan_scoped_revalidation(["paper/main.tex"], "cosmetic", "delivery")
        self.assertEqual(local["stages"], ["paper"])
        self.assertEqual(semantic["stages"], ["model-design", "computation", "validation", "paper", "delivery"])
        self.assertEqual(cosmetic["stages"], ["paper", "delivery"])
        self.assertFalse(local["full_workspace_audit"])

    def test_matlab_is_selected_for_matlab_fit_on_a_tie_break(self):
        result = select_backend(
            {"features": ["numerical_linear_algebra", "optimization"]},
            {"preferred": "matlab", "fallback": "python", "selection": "auto"},
            {"matlab": True, "python": True},
        )
        self.assertEqual(result["selected_language"], "matlab")
        self.assertTrue(result["single_backend_policy"])

    def test_python_is_selected_when_task_fit_is_clear(self):
        result = select_backend(
            {"features": ["data_cleaning", "csv_excel"]},
            {"preferred": "matlab", "fallback": "python", "selection": "auto"},
            {"matlab": True, "python": True},
        )
        self.assertEqual(result["selected_language"], "python")

    def test_matlab_preferred_falls_back_to_python_when_unavailable(self):
        result = select_backend(
            {"features": ["optimization"]},
            {"preferred": "matlab", "fallback": "python", "selection": "auto"},
            {"matlab": False, "python": True},
        )
        self.assertEqual(result["selected_language"], "python")
        self.assertEqual(result["fallback_from"], "matlab")

    def test_paper_handoff_stale_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v04_project(root)
            path = root / "validation" / "CLAIM_LEDGER.json"
            claims = json.loads(path.read_text(encoding="utf-8"))
            claims["claims"][0]["text"] += " Changed upstream."
            write_json(root, "validation/CLAIM_LEDGER.json", claims)
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("HANDOFF-E003", {item.rule_id for item in findings})

    def test_paper_handoff_excludes_full_run_history(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v04_project(root)
            handoff = json.loads((root / "handoffs" / "validation-paper" / "HANDOFF.json").read_text(encoding="utf-8"))
            self.assertFalse(any(item["path"].startswith("runs/") for item in handoff["canonical_artifacts"]))
            self.assertEqual(
                set(handoff["payload"]),
                {"problem_summary", "model_summary", "verified_results", "claims", "limitations", "figure_table_plan", "official_format_files"},
            )
            self.assertIn("debug transcripts", handoff["excluded_history"])

    def test_handoffs_bind_only_canonical_downstream_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v04_project(root)
            modeling = json.loads((root / "handoffs" / "modeling-computation" / "HANDOFF.json").read_text(encoding="utf-8"))
            computation = json.loads((root / "handoffs" / "computation-validation" / "HANDOFF.json").read_text(encoding="utf-8"))
            modeling_paths = {item["path"] for item in modeling["canonical_artifacts"]}
            computation_roles = {item["role"] for item in computation["canonical_artifacts"]}
            self.assertIn("problem/SOURCE_MANIFEST.json", modeling_paths)
            self.assertIn("problem/official/problem.txt", modeling_paths)
            self.assertTrue({"official_run", "computation_source", "claim_bearing_output"}.issubset(computation_roles))
            self.assertNotIn("run_log", computation_roles)

    def test_official_run_is_bound_to_executed_source_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            (root / "code" / "solve.py").write_text("print('stale')\n", encoding="utf-8")
            findings, _ = check_project(root, "computation", "strict")
            self.assertIn("RUN-E020", {item.rule_id for item in findings})

    def test_review_package_detects_upstream_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_project(root)
            shutil.rmtree(root / "validation" / "independent-review-package")
            (root / "validation" / "INDEPENDENT_REVIEW_RESULT.json").unlink()
            (root / "validation" / "INDEPENDENT_REVIEW_RAW.md").unlink()
            (root / "model" / "VALIDATION_PLAN.md").write_text("# Validation plan\n", encoding="utf-8")
            build_review_package(root)
            (root / "code" / "solve.py").write_text("print('changed upstream')\n", encoding="utf-8")
            findings, _ = check_project(root, "validation", "strict")
            self.assertIn("IREVIEW-E025", {item.rule_id for item in findings})

    def test_visible_local_paths_cover_unix_and_windows_home_directories(self):
        blocking, _ = inspect_text(r"/home/alice/project/output.json C:\Users\alice\project\result.json")
        self.assertTrue(any(item["rule_id"] == "PAPER-TEXT-E004" for item in blocking))

    def test_latex_commit_rolls_back_partial_publish(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            staging = root / "staging"
            paper = root / "paper"
            staging.mkdir()
            (staging / "a.tex").write_text("a", encoding="utf-8")
            (staging / "b.tex").write_text("b", encoding="utf-8")
            real_replace = __import__("os").replace
            calls = 0

            def flaky(source, destination):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("fixture commit failure")
                return real_replace(source, destination)

            with mock.patch("init_latex_paper.os.replace", side_effect=flaky):
                with self.assertRaises(OSError):
                    commit_staged_tree(staging, paper)
            self.assertEqual(list(paper.iterdir()), [])

    def test_v04_migration_preserves_source_and_requires_official_rerun(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "v04"
            target = root / "v05"
            source.mkdir()
            build_valid_project(source)
            for path in source.rglob("*.json"):
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict) and data.get("schema_version") == "0.5.0":
                    data["schema_version"] = "0.4.0"
                    if isinstance(data.get("producer"), dict):
                        data["producer"]["version"] = "0.4.0"
                    if data.get("artifact_type") == "workflow_state":
                        data["workflow_version"] = "0.4.0"
                        data.pop("mode", None)
                        data.pop("implementation", None)
                    if data.get("artifact_type") == "run_manifest":
                        data.pop("official_run", None)
                        data.pop("implementation", None)
                    write_json(source, path.relative_to(source).as_posix(), data)
            original_code = (source / "code" / "solve.py").read_bytes()
            report_path = migrate(source, target)
            state = json.loads((target / ".cumcm/state.json").read_text(encoding="utf-8"))
            run = json.loads((target / "runs/RUN-Q1-001/RUN_MANIFEST.json").read_text(encoding="utf-8"))
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(state["workflow_version"], "0.5.0")
            self.assertEqual(state["mode"], "working")
            self.assertFalse(run["official_run"])
            self.assertFalse(report["official_runs_recertified"])
            self.assertEqual((source / "code" / "solve.py").read_bytes(), original_code)


if __name__ == "__main__":
    unittest.main()
