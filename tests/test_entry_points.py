"""Guards for the two entry points and for the vocabulary v0.6 removed."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / ".agents" / "skills" / "cumcm-workflow"
CLAUDE_SKILL = ROOT / ".claude" / "skills" / "cumcm-workflow" / "SKILL.md"
SCRIPTS = CANONICAL / "scripts"

REMOVED_VOCABULARY = (
    "PAPER_TRACEABILITY",
    "paper-traceability",
    "conclusions_withheld",
    "plan_scoped_revalidation",
    "--profile",
    "awaiting_review\"",
)


def frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, f"{path} has no YAML frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        if value.strip():
            fields[key.strip()] = value.strip()
    return fields


class EntryPointTests(unittest.TestCase):
    def test_both_entry_points_declare_the_same_skill(self):
        codex = frontmatter(CANONICAL / "SKILL.md")
        claude = frontmatter(CLAUDE_SKILL)
        self.assertEqual(codex["name"], "cumcm-workflow")
        self.assertEqual(claude["name"], "cumcm-workflow")
        for field in ("name", "description"):
            self.assertIn(field, claude, "Claude Code requires name and description in the frontmatter")
        self.assertGreater(len(claude["description"]), 40)

    def test_claude_router_points_at_the_canonical_tree_and_real_scripts(self):
        text = CLAUDE_SKILL.read_text(encoding="utf-8")
        self.assertIn(".agents/skills/cumcm-workflow/SKILL.md", text)
        referenced = set(re.findall(r"\$S/([a-z_]+\.py)", text)) | set(re.findall(r"scripts/([a-z_]+\.py)", text))
        self.assertTrue(referenced)
        for name in sorted(referenced):
            with self.subTest(script=name):
                self.assertTrue((SCRIPTS / name).is_file(), f"router names a script that does not exist: {name}")

    def test_codex_manifest_still_present(self):
        manifest = CANONICAL / "agents" / "openai.yaml"
        self.assertTrue(manifest.is_file(), "the Codex entry point must survive the Claude Code addition")
        self.assertIn("cumcm-workflow", manifest.read_text(encoding="utf-8"))

    def test_every_referenced_reference_file_exists(self):
        text = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        for name in sorted(set(re.findall(r"\(references/([a-z0-9-]+\.md)\)", text))):
            with self.subTest(reference=name):
                self.assertTrue((CANONICAL / "references" / name).is_file())

    def test_scripts_named_in_the_canonical_skill_exist(self):
        text = (CANONICAL / "SKILL.md").read_text(encoding="utf-8")
        for name in sorted(set(re.findall(r"scripts/([a-z_0-9]+\.py)", text))):
            with self.subTest(script=name):
                self.assertTrue((SCRIPTS / name).is_file())


class RemovedVocabularyTests(unittest.TestCase):
    """Instruction files must not tell an agent to produce something v0.6 deleted.

    Design and migration documents are exempt on purpose: explaining what was
    removed is exactly their job.
    """

    def instruction_files(self) -> list[Path]:
        paths = [CANONICAL / "SKILL.md", CLAUDE_SKILL, ROOT / "CLAUDE.md"]
        paths += sorted((CANONICAL / "assets").rglob("*.md"))
        return paths

    def test_instruction_files_do_not_promise_removed_features(self):
        for path in self.instruction_files():
            text = path.read_text(encoding="utf-8")
            for token in REMOVED_VOCABULARY:
                with self.subTest(document=path.name, token=token):
                    self.assertNotIn(token, text)

    def test_readmes_do_not_document_the_deleted_profile_flag(self):
        for name in ("README.md", "README.en.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(document=name):
                self.assertNotIn("--profile", text)

    def test_scripts_and_schemas_do_not_mention_removed_contracts(self):
        for path in sorted(SCRIPTS.glob("*.py")) + sorted((CANONICAL / "schemas").glob("*.json")):
            text = path.read_text(encoding="utf-8")
            for token in ("PAPER_TRACEABILITY", "conclusions_withheld", "PROFILES"):
                with self.subTest(path=path.name, token=token):
                    self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
