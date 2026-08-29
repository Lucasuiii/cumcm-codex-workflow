from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".agents" / "skills" / "cumcm-workflow" / "scripts" / "migrate_v01.py"
sys.path.insert(0, str(SCRIPT.parent))
SPEC = importlib.util.spec_from_file_location("migrate_v01", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class MigrationTests(unittest.TestCase):
    def test_state_migration_backs_up_and_does_not_infer_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state_path = root / ".cumcm" / "state.json"
            state_path.parent.mkdir()
            old = {
                "current_stage": "problem-analysis",
                "stages": {
                    "intake": "passed",
                    "problem-analysis": "in_progress",
                    "model-design": "not_started",
                    "computation": "not_started",
                    "validation": "not_started",
                    "paper": "not_started",
                    "delivery": "not_started",
                },
            }
            state_path.write_text(json.dumps(old), encoding="utf-8")
            MODULE.migrate_state(root)
            self.assertEqual(json.loads((root / ".cumcm" / "state.v0.1.json").read_text(encoding="utf-8")), old)
            migrated = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(migrated["workflow_version"], "0.2.0")
            self.assertEqual(migrated["review"]["decision"], "unreviewed")
            self.assertFalse((root / "analysis" / "TASK_CAPABILITIES.json").exists())

    def test_existing_backup_stops_second_state_migration(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            state_path = root / ".cumcm" / "state.json"
            state_path.parent.mkdir()
            state_path.write_text(json.dumps({"current_stage": "intake", "stages": {"intake": "in_progress"}}), encoding="utf-8")
            (root / ".cumcm" / "state.v0.1.json").write_text("{}", encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.migrate_state(root)


if __name__ == "__main__":
    unittest.main()
