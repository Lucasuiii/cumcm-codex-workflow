#!/usr/bin/env python3
"""Initialize a modular v0.3 CUMCM LaTeX paper without overwriting existing work."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKFLOW_VERSION = "0.3.0"
TEMPLATE_ID = "cumcm-generic-ctex"


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return slug or "question"


def render(template: str, values: dict[str, str]) -> str:
    result = template
    for key, value in values.items():
        result = result.replace(f"@@{key}@@", value)
    unresolved = sorted(set(re.findall(r"@@[A-Z0-9_]+@@", result)))
    if unresolved:
        raise ValueError(f"unresolved template tokens: {', '.join(unresolved)}")
    return result


def validate_inputs(project: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    state = read_object(project / ".cumcm" / "state.json")
    facts = read_object(project / "analysis" / "PROBLEM_FACTS.json")
    plan = read_object(project / "paper" / "PAPER_PLAN.json")
    if state.get("workflow_version") != WORKFLOW_VERSION or state.get("schema_version") != WORKFLOW_VERSION:
        raise ValueError("LaTeX initialization requires an exact v0.3 workflow state")
    project_ids = {state.get("project_id"), facts.get("project_id"), plan.get("project_id")}
    if None in project_ids or len(project_ids) != 1:
        raise ValueError("state, problem facts, and paper plan must share one project_id")
    subproblems = facts.get("subproblems")
    if not isinstance(subproblems, list) or not subproblems:
        raise ValueError("PROBLEM_FACTS.json must contain at least one subproblem")
    fact_ids = {
        str(item.get("subproblem_id") or item.get("id"))
        for item in subproblems
        if isinstance(item, dict) and (item.get("subproblem_id") or item.get("id"))
    }
    plan_ids = {
        str(item.get("subproblem_id"))
        for item in plan.get("question_argument_chains", [])
        if isinstance(item, dict) and item.get("subproblem_id")
    }
    if fact_ids != plan_ids:
        raise ValueError("paper plan argument chains must exactly cover the problem-fact subproblems")
    return state, facts, plan


def initialize(project: Path, title: str, competition_year: int, keywords: str) -> Path:
    state, facts, _ = validate_inputs(project)
    skill_root = Path(__file__).resolve().parents[1]
    template_root = skill_root / "assets" / "latex-template" / "generic-ctex"
    template_meta = read_object(template_root / "template.json")
    paper_dir = project / "paper"
    protected_targets = [paper_dir / "main.tex", paper_dir / "metadata.tex", paper_dir / "macros.tex", paper_dir / "sections", paper_dir / "LATEX_TEMPLATE_MANIFEST.json"]
    conflicts = [path for path in protected_targets if path.exists()]
    if conflicts:
        listed = ", ".join(path.relative_to(project).as_posix() for path in conflicts)
        raise ValueError(f"refusing to overwrite existing paper sources: {listed}")

    subproblems = [item for item in facts["subproblems"] if isinstance(item, dict)]
    question_records: list[dict[str, str]] = []
    question_inputs: list[str] = []
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    temp_parent = project / ".cumcm" / "tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="latex-init-", dir=temp_parent) as temp:
        staging = Path(temp) / "paper"
        sections = staging / "sections"
        sections.mkdir(parents=True)
        for source in sorted((template_root / "sections").glob("*.tex")):
            shutil.copy2(source, sections / source.name)
        shutil.copy2(template_root / "macros.tex", staging / "macros.tex")
        shutil.copy2(template_root / "references.bib", staging / "references.bib")

        question_template = (template_root / "question.tex.tmpl").read_text(encoding="utf-8")
        for index, item in enumerate(subproblems, 1):
            subproblem_id = str(item.get("subproblem_id") or item.get("id"))
            request = str(item.get("request") or subproblem_id)
            filename = f"{index * 10:02d}_question_{safe_slug(subproblem_id)}.tex"
            rel = f"paper/sections/{filename}"
            content = render(
                question_template,
                {
                    "QUESTION_TITLE": latex_escape(f"{subproblem_id}：{request}"),
                    "SUBPROBLEM_ID": subproblem_id,
                },
            )
            (sections / filename).write_text(content, encoding="utf-8")
            question_records.append({"subproblem_id": subproblem_id, "path": rel})
            question_inputs.append(f"\\input{{sections/{filename[:-4]}}}")

        main_text = render(
            (template_root / "main.tex.tmpl").read_text(encoding="utf-8"),
            {"QUESTION_INPUTS": "\n".join(question_inputs)},
        )
        metadata_text = render(
            (template_root / "metadata.tex.tmpl").read_text(encoding="utf-8"),
            {
                "PROJECT_ID": str(state["project_id"]),
                "TITLE": latex_escape(title),
                "COMPETITION_YEAR": str(competition_year),
                "KEYWORDS": latex_escape(keywords),
            },
        )
        (staging / "main.tex").write_text(main_text, encoding="utf-8")
        (staging / "metadata.tex").write_text(metadata_text, encoding="utf-8")

        section_files = sorted(f"paper/sections/{path.name}" for path in sections.glob("*.tex"))
        required_files = ["paper/main.tex", "paper/metadata.tex", "paper/macros.tex", "paper/references.bib", *section_files]
        manifest = {
            "schema_version": WORKFLOW_VERSION,
            "artifact_type": "latex_template_manifest",
            "project_id": state["project_id"],
            "updated_at": generated_at,
            "producer": {"kind": "script", "name": "init_latex_paper.py", "version": WORKFLOW_VERSION},
            "review": {"decision": "unreviewed", "reviewer": None, "reviewed_at": None, "scope": "generated LaTeX scaffold", "notes": None},
            "template_id": template_meta["template_id"],
            "template_version": template_meta["template_version"],
            "mode": template_meta["mode"],
            "engine": template_meta["engine"],
            "competition": "CUMCM",
            "competition_year": competition_year,
            "official_compliance": "unverified",
            "official_template_source": None,
            "main_path": "paper/main.tex",
            "metadata_path": "paper/metadata.tex",
            "section_files": section_files,
            "subproblem_sections": question_records,
            "required_files": required_files,
            "placeholder_markers": ["CUMCM-TODO", "\\placeholder{"],
            "template_source": f"repo_asset:{TEMPLATE_ID}@{WORKFLOW_VERSION}",
        }
        (staging / "LATEX_TEMPLATE_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        paper_dir.mkdir(parents=True, exist_ok=True)
        for source in staging.iterdir():
            destination = paper_dir / source.name
            if source.is_dir():
                shutil.copytree(source, destination)
            else:
                shutil.copy2(source, destination)

    return paper_dir / "LATEX_TEMPLATE_MANIFEST.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize the canonical modular LaTeX scaffold for a v0.3 CUMCM project")
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--title", default="全国大学生数学建模竞赛论文")
    parser.add_argument("--competition-year", type=int, default=datetime.now().year)
    parser.add_argument("--keywords", default="数学建模；可复现计算；证据链")
    args = parser.parse_args()
    project = args.project.resolve()
    if not project.is_dir():
        parser.error(f"project is not a directory: {project}")
    try:
        manifest = initialize(project, args.title, args.competition_year, args.keywords)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"initialized modular LaTeX paper: {manifest}")
    print("official format compliance remains unverified until checked against the current competition package and rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
