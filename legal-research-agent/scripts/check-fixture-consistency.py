#!/usr/bin/env python3
"""Check consistency between case fixtures, quality specs, and golden outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASE_DIR = ROOT / "tests" / "fixtures" / "cases"
DEFAULT_QUALITY_DIR = ROOT / "tests" / "fixtures" / "quality"
DEFAULT_GOLDEN_DIR = ROOT / "tests" / "fixtures" / "golden-set"
DEFAULT_TAXONOMY_PATH = ROOT / "knowledge" / "game-regulation" / "issue-taxonomy.md"
AGENT_ID = "legal-research-agent"


def result_question(result_text: str) -> str:
    lines = result_text.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != "## Question":
            continue
        collected: list[str] = []
        for body_line in lines[index + 1 :]:
            if body_line.startswith("## "):
                break
            if body_line.strip():
                collected.append(body_line.strip())
        return "\n".join(collected).strip()
    return ""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_case_fixtures(case_dir: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    cases: dict[str, dict[str, Any]] = {}
    for path in sorted(case_dir.glob("*.json")):
        data = load_json(path)
        if not isinstance(data, dict):
            errors.append(f"{path}: case fixture must be object")
            continue
        case_id = data.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{path}: missing non-empty id")
            continue
        if case_id in cases:
            errors.append(f"{path}: duplicate case id {case_id!r}")
        cases[case_id] = {"path": path, "data": data}
    return cases, errors


def load_quality_specs(quality_dir: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    specs: dict[str, dict[str, Any]] = {}
    spec_ids: set[str] = set()
    for path in sorted(quality_dir.glob("*-quality-spec.json")):
        data = load_json(path)
        if not isinstance(data, dict):
            errors.append(f"{path}: quality spec must be object")
            continue
        spec_id = data.get("id")
        if not isinstance(spec_id, str) or not spec_id:
            errors.append(f"{path}: missing non-empty id")
        elif spec_id in spec_ids:
            errors.append(f"{path}: duplicate spec id {spec_id!r}")
        else:
            spec_ids.add(spec_id)
        case_id = data.get("case_id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{path}: missing non-empty case_id")
            continue
        if case_id in specs:
            errors.append(f"{path}: duplicate quality spec for case_id {case_id!r}")
        specs[case_id] = {"path": path, "data": data}
    return specs, errors


def golden_case_ids(golden_dir: Path) -> set[str]:
    if not golden_dir.exists():
        return set()
    return {path.name for path in golden_dir.iterdir() if path.is_dir()}


def taxonomy_headings(taxonomy_path: Path) -> set[str]:
    if not taxonomy_path.exists():
        return set()
    headings: set[str] = set()
    for line in taxonomy_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            heading = line.removeprefix("## ").strip()
            if heading:
                headings.add(heading)
    return headings


def compare_list_field(
    errors: list[str],
    case_id: str,
    field_name: str,
    case_data: dict[str, Any],
    spec_data: dict[str, Any],
    spec_field_name: str | None = None,
) -> None:
    spec_field_name = spec_field_name or f"required_{field_name}"
    case_values = set(str(value) for value in case_data.get(field_name, []) if str(value))
    spec_values = set(str(value) for value in spec_data.get(spec_field_name, []) if str(value))
    missing = sorted(case_values - spec_values)
    if missing:
        errors.append(
            f"{case_id}: quality spec {spec_field_name} missing values from case {field_name}: {missing}"
        )


def compare_bool_field(
    errors: list[str],
    case_id: str,
    field_name: str,
    case_data: dict[str, Any],
    spec_data: dict[str, Any],
    spec_field_name: str | None = None,
) -> None:
    spec_field_name = spec_field_name or field_name
    case_value = bool(case_data.get(field_name, False))
    spec_value = bool(spec_data.get(spec_field_name, False))
    if case_value != spec_value:
        errors.append(
            f"{case_id}: {field_name} mismatch between case ({case_value!r}) "
            f"and quality spec {spec_field_name} ({spec_value!r})"
        )


def check_consistency(
    case_dir: Path = DEFAULT_CASE_DIR,
    quality_dir: Path = DEFAULT_QUALITY_DIR,
    golden_dir: Path = DEFAULT_GOLDEN_DIR,
    taxonomy_path: Path = DEFAULT_TAXONOMY_PATH,
    agent_id: str = AGENT_ID,
) -> list[str]:
    errors: list[str] = []
    for directory, label in ((case_dir, "case"), (quality_dir, "quality"), (golden_dir, "golden-set")):
        if not directory.exists():
            errors.append(f"{label} directory does not exist: {directory}")

    if errors:
        return errors

    cases, case_errors = load_case_fixtures(case_dir)
    specs, spec_errors = load_quality_specs(quality_dir)
    errors.extend(case_errors)
    errors.extend(spec_errors)
    golden_ids = golden_case_ids(golden_dir)
    known_taxonomy = taxonomy_headings(taxonomy_path)

    if not cases:
        errors.append(f"no case fixtures found in {case_dir}")
    if not specs:
        errors.append(f"no quality specs found in {quality_dir}")
    if not golden_ids:
        errors.append(f"no golden-set output directories found in {golden_dir}")

    case_ids = set(cases)
    spec_case_ids = set(specs)

    for case_id in sorted(case_ids - spec_case_ids):
        errors.append(f"{case_id}: missing quality spec")
    for case_id in sorted(spec_case_ids - case_ids):
        errors.append(f"{case_id}: quality spec has no matching case fixture")
    for case_id in sorted(case_ids - golden_ids):
        errors.append(f"{case_id}: missing golden-set output directory")
    for case_id in sorted(golden_ids - case_ids):
        errors.append(f"{case_id}: golden-set output has no matching case fixture")

    for case_id in sorted(case_ids & spec_case_ids):
        case_data = cases[case_id]["data"]
        spec_data = specs[case_id]["data"]
        expected_mode = case_data.get("expected_research_mode")
        spec_mode = spec_data.get("expected_research_mode")
        if expected_mode != spec_mode:
            errors.append(
                f"{case_id}: expected_research_mode mismatch between case ({expected_mode!r}) "
                f"and quality spec ({spec_mode!r})"
            )
        compare_list_field(errors, case_id, "jurisdictions", case_data, spec_data)
        compare_list_field(errors, case_id, "domains", case_data, spec_data)
        compare_list_field(errors, case_id, "required_taxonomy", case_data, spec_data, "required_taxonomy")
        compare_bool_field(errors, case_id, "requires_comparison_matrix", case_data, spec_data)

        for taxonomy in case_data.get("required_taxonomy", []):
            if known_taxonomy and taxonomy not in known_taxonomy:
                errors.append(f"{case_id}: unknown required_taxonomy value {taxonomy!r}")
        for taxonomy in spec_data.get("required_taxonomy", []):
            if known_taxonomy and taxonomy not in known_taxonomy:
                errors.append(f"{case_id}: quality spec has unknown required_taxonomy value {taxonomy!r}")

    for case_id in sorted(case_ids & golden_ids):
        output_dir = golden_dir / case_id
        result_path = output_dir / f"{agent_id}-result.md"
        meta_path = output_dir / f"{agent_id}-meta.json"
        if not result_path.exists():
            errors.append(f"{case_id}: missing golden result file {result_path.name}")
        else:
            expected_question = str(cases[case_id]["data"].get("user_question", "")).strip()
            displayed_question = result_question(result_path.read_text(encoding="utf-8"))
            if expected_question and displayed_question != expected_question:
                errors.append(
                    f"{case_id}: golden result question mismatch "
                    f"case={expected_question!r} result={displayed_question!r}"
                )
        if not meta_path.exists():
            errors.append(f"{case_id}: missing golden metadata file {meta_path.name}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case-dir", type=Path, default=DEFAULT_CASE_DIR)
    parser.add_argument("--quality-dir", type=Path, default=DEFAULT_QUALITY_DIR)
    parser.add_argument("--golden-dir", type=Path, default=DEFAULT_GOLDEN_DIR)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY_PATH)
    parser.add_argument("--agent-id", default=AGENT_ID)
    args = parser.parse_args(argv)

    errors = check_consistency(args.case_dir, args.quality_dir, args.golden_dir, args.taxonomy, args.agent_id)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: fixture consistency valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
