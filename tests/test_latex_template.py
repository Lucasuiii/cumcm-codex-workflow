from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "cumcm-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from init_latex_paper import initialize  # noqa: E402
from test_v03_paper_quality import build_valid_v03_project  # noqa: E402
from test_workflow_core import envelope, write_json  # noqa: E402
from workflow_checks import check_project  # noqa: E402


def build_inputs(root: Path, problem_ids: tuple[str, ...] = ("Q1", "Q2"), plan_ids: tuple[str, ...] | None = None) -> None:
    state = envelope("workflow_state")
    state.update(
        {
            "workflow_version": "0.3.0",
            "current_stage": "paper",
            "stages": {
                "intake": "passed",
                "problem-analysis": "passed",
                "model-design": "passed",
                "computation": "passed",
                "validation": "passed",
                "paper": "in_progress",
                "delivery": "not_started",
            },
        }
    )
    write_json(root, ".cumcm/state.json", state)
    facts = envelope("problem_facts")
    facts.update(
        {
            "subproblems": [
                {"subproblem_id": ident, "request": f"Solve {ident}", "expected_output": f"Result {ident}"}
                for ident in problem_ids
            ],
            "facts": [],
            "definitions": [],
            "ambiguities": [],
            "assumptions": [],
        }
    )
    write_json(root, "analysis/PROBLEM_FACTS.json", facts)
    layer = {"status": "included", "summary": "planned", "evidence_ids": [], "rationale": None}
    plan = envelope("paper_plan")
    plan.update(
        {
            "reference_reviews": [],
            "claims_evidence_matrix": [],
            "question_argument_chains": [
                {
                    "subproblem_id": ident,
                    "layers": {
                        name: dict(layer)
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
                for ident in (plan_ids if plan_ids is not None else problem_ids)
            ],
            "figure_plan": [],
            "page_budget": [{"section": "paper", "purpose": "complete argument", "target_pages": 8.0}],
        }
    )
    write_json(root, "paper/PAPER_PLAN.json", plan)


class LatexTemplateTests(unittest.TestCase):
    def test_dynamic_sections_and_manifest_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_inputs(root)
            manifest_path = initialize(root, "2026 B test", 2026, "model; validation")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(
                {item["subproblem_id"] for item in manifest["subproblem_sections"]},
                {"Q1", "Q2"},
            )
            for rel in manifest["required_files"]:
                self.assertTrue((root / rel).is_file(), rel)
            main = (root / manifest["main_path"]).read_text(encoding="utf-8")
            self.assertIn(r"\input{sections/10_question_q1}", main)
            self.assertIn(r"\input{sections/20_question_q2}", main)

    def test_refuses_to_overwrite_existing_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_inputs(root)
            initialize(root, "first", 2026, "first")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                initialize(root, "second", 2026, "second")

    def test_plan_must_exactly_cover_problem_questions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_inputs(root, problem_ids=("Q1", "Q2"), plan_ids=("Q1",))
            with self.assertRaisesRegex(ValueError, "exactly cover"):
                initialize(root, "mismatch", 2026, "mismatch")

    def test_final_placeholder_blocks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            section = root / "paper" / "sections" / "10_question_q1.tex"
            section.write_text(section.read_text(encoding="utf-8") + "\n% CUMCM-TODO\n", encoding="utf-8")
            findings, _ = check_project(root, "paper", "strict")
            self.assertIn("LATEX-E008", {item.rule_id for item in findings})

    def test_delivery_requires_current_official_format_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "paper" / "LATEX_TEMPLATE_MANIFEST.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            manifest["official_compliance"] = "unverified"
            manifest["official_template_source"] = None
            write_json(root, "paper/LATEX_TEMPLATE_MANIFEST.json", manifest)
            findings, _ = check_project(root, "delivery", "strict", "preflight")
            item = next(item for item in findings if item.rule_id == "LATEX-E009")
            self.assertTrue(item.gate_only)

    def test_compile_engine_must_match_template(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            build_valid_v03_project(root)
            path = root / "delivery" / "COMPILE_RECEIPT.json"
            receipt = json.loads(path.read_text(encoding="utf-8"))
            receipt["attempts"][0]["engine"] = "lualatex"
            write_json(root, "delivery/COMPILE_RECEIPT.json", receipt)
            findings, _ = check_project(root, "delivery", "strict")
            self.assertIn("COMPILE-E014", {item.rule_id for item in findings})


if __name__ == "__main__":
    unittest.main()
