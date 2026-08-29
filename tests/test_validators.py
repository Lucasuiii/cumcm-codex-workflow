from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / ".agents" / "skills" / "cumcm-workflow" / "scripts"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ValidatorTests(unittest.TestCase):
    def test_inventory_hashes_files_and_excludes_output(self):
        module = load("inventory_artifacts")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "problem.pdf").write_bytes(b"official")
            output = root / "SOURCE_MANIFEST.json"
            records = module.inventory(root, output)
            self.assertEqual([r["path"] for r in records], ["problem.pdf"])
            self.assertEqual(records[0]["sha256"], hashlib.sha256(b"official").hexdigest())

    def test_stage_state_accepts_complete_state(self):
        module = load("validate_stage_state")
        data = {
            "current_stage": "problem-analysis",
            "stages": {stage: "not_started" for stage in module.STAGES},
        }
        data["stages"]["intake"] = "passed"
        data["stages"]["problem-analysis"] = "in_progress"
        self.assertEqual(module.validate(data), [])
        data["stages"]["problem-analysis"] = "unknown"
        self.assertTrue(module.validate(data))
        data["stages"]["problem-analysis"] = "in_progress"
        data["stages"]["model-design"] = "passed"
        self.assertTrue(module.validate(data))

    def test_problem_facts_require_traceable_fields(self):
        module = load("validate_problem_facts")
        good = {
            "problem_id": "2024-B",
            "source_files": ["problem/B.pdf"],
            "subproblems": [{"id": "Q1", "request": "design a sampling plan"}],
            "facts": [{"id": "F1", "statement": "stated threshold", "source": "problem/B.pdf#page=1"}],
        }
        self.assertEqual(module.validate(good), [])
        good["facts"][0]["source"] = ""
        self.assertIn("fact 0 missing source", module.validate(good))
        good["facts"][0]["source"] = "problem/other.pdf#page=1"
        self.assertTrue(any("unregistered source" in error for error in module.validate(good)))

    def test_run_manifest_requires_real_output(self):
        module = load("validate_results")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "runs" / "r1" / "outputs" / "result.json"
            output.parent.mkdir(parents=True)
            output.write_text("{}", encoding="utf-8")
            data = {
                "run_id": "r1",
                "command": "python code/q1.py",
                "status": "completed",
                "started_at": "2026-01-01T00:00:00Z",
                "finished_at": "2026-01-01T00:01:00Z",
                "exit_code": 0,
                "inputs": [],
                "outputs": ["runs/r1/outputs/result.json"],
            }
            self.assertEqual(module.validate(data, root), [])
            output.unlink()
            self.assertTrue(module.validate(data, root))

    def test_supported_claim_requires_existing_evidence(self):
        module = load("trace_claims")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            evidence = root / "results" / "q1.json"
            evidence.parent.mkdir()
            evidence.write_text("{}", encoding="utf-8")
            data = {
                "claims": [
                    {
                        "id": "C1",
                        "claim": "The saved run supports the local result.",
                        "status": "supported",
                        "evidence": ["results/q1.json"],
                    }
                ]
            }
            self.assertEqual(module.validate(data, root), [])
            data["claims"][0]["evidence"] = []
            self.assertTrue(module.validate(data, root))

    def test_delivery_hash_must_match(self):
        module = load("verify_delivery")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paper = root / "paper.pdf"
            paper.write_bytes(b"pdf")
            digest = hashlib.sha256(b"pdf").hexdigest()
            data = {"files": [{"path": "paper.pdf", "sha256": digest}]}
            self.assertEqual(module.validate(data, root), [])
            data["files"][0]["sha256"] = "0" * 64
            self.assertIn("hash mismatch: paper.pdf", module.validate(data, root))


if __name__ == "__main__":
    unittest.main()
