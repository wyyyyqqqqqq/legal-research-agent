#!/usr/bin/env python3
"""Evaluate legal-output quality beyond JSON contract shape.

The validator answers "is the metadata well formed?".
This evaluator asks a narrower but more important question:
"does the output preserve minimum legal-research quality?"
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate-output.py"
STRUCTURE_CHECK_PATH = ROOT / "scripts" / "check-result-structure.py"
AGENT_ID = "legal-research-agent"
PASS = "pass"
FAIL = "fail"
LIMITING_CONFIDENCE_GAP_TYPES = {
    "classification_mismatch",
    "jurisdiction",
    "other",
    "source_access",
    "source_coverage",
    "temporal_status",
}
SOURCE_ID_PATTERN = re.compile(r"\bsrc_[0-9A-Za-z_-]+\b")


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_output", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load validate-output.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def load_structure_checker():
    spec = importlib.util.spec_from_file_location("check_result_structure", STRUCTURE_CHECK_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-result-structure.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


STRUCTURE_CHECKER = load_structure_checker()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_terms(values: Any) -> list[str]:
    if values is None:
        return []
    if not isinstance(values, list):
        values = [values]
    return [str(value).strip().lower() for value in values if str(value).strip()]


def text_blob(meta: dict[str, Any], result_text: str) -> str:
    chunks: list[str] = [result_text, str(meta.get("summary", ""))]
    chunks.extend(str(item) for item in meta.get("key_findings", []) if item is not None)
    for issue in meta.get("issue_map", []):
        if isinstance(issue, dict):
            chunks.append(str(issue.get("issue", "")))
            chunks.append(str(issue.get("answer", "")))
    for gap in meta.get("coverage_gaps", []):
        chunks.append(json.dumps(gap, ensure_ascii=False) if isinstance(gap, dict) else str(gap))
    return "\n".join(chunks).lower()


def source_by_id(meta: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources: dict[str, dict[str, Any]] = {}
    for source in meta.get("sources", []):
        if isinstance(source, dict) and isinstance(source.get("id"), str):
            sources[source["id"]] = source
    return sources


def issue_authority_grades(issue: dict[str, Any], sources: dict[str, dict[str, Any]]) -> list[str]:
    grades: list[str] = []
    for source_id in issue.get("authority_ids", []):
        source = sources.get(str(source_id))
        if source:
            grades.append(str(source.get("grade", "")))
    return grades


def has_any_grade(grades: list[str], allowed: set[str]) -> bool:
    return any(grade in allowed for grade in grades)


def referenced_source_ids(value: str) -> set[str]:
    return set(SOURCE_ID_PATTERN.findall(value))


def coverage_gap_types(meta: dict[str, Any]) -> set[str]:
    return {
        str(gap.get("type", "")).lower()
        for gap in meta.get("coverage_gaps", [])
        if isinstance(gap, dict) and str(gap.get("type", "")).strip()
    }


def confidence_limiting_reasons(meta: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if meta.get("error") is not None:
        reasons.append(f"error={meta.get('error')}")
    if meta.get("research_mode") == "fallback":
        reasons.append("research_mode=fallback")
    limiting_gaps = sorted(coverage_gap_types(meta) & LIMITING_CONFIDENCE_GAP_TYPES)
    if limiting_gaps:
        reasons.append(f"coverage_gaps={','.join(limiting_gaps)}")
    return reasons


def key_finding_source_errors(meta: dict[str, Any], sources: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    known_source_ids = set(sources)
    for index, finding in enumerate(meta.get("key_findings", [])):
        if not isinstance(finding, str):
            continue
        source_ids = referenced_source_ids(finding)
        if not source_ids:
            errors.append(f"key_findings[{index}]: must cite at least one metadata source id")
            continue
        unknown_source_ids = sorted(source_ids - known_source_ids)
        if unknown_source_ids:
            errors.append(
                f"key_findings[{index}]: references unknown source ids {unknown_source_ids}"
            )
    return errors


def comparison_jurisdictions(meta: dict[str, Any], case_spec: dict[str, Any]) -> list[str]:
    raw_values = case_spec.get("required_jurisdictions") or meta.get("jurisdictions", [])
    if not isinstance(raw_values, list):
        raw_values = [raw_values]
    jurisdictions: list[str] = []
    seen: set[str] = set()
    for value in raw_values:
        normalized = str(value).strip()
        key = normalized.lower()
        if normalized and key not in seen:
            jurisdictions.append(normalized)
            seen.add(key)
    return jurisdictions


def comparison_matrix_errors(meta: dict[str, Any], case_spec: dict[str, Any]) -> list[str]:
    matrix = meta.get("comparison_matrix")
    if not isinstance(matrix, list) or not matrix:
        return ["comparison_matrix: expected for this case but missing or empty"]

    errors: list[str] = []
    jurisdictions = comparison_jurisdictions(meta, case_spec)
    if len(jurisdictions) < 2:
        errors.append("comparison_matrix: requires at least two jurisdictions to compare")

    for index, row in enumerate(matrix):
        field = f"comparison_matrix[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{field}: expected object row")
            continue
        if not isinstance(row.get("issue"), str) or not row.get("issue", "").strip():
            errors.append(f"{field}.issue: expected non-empty string")
        if not isinstance(row.get("status"), str) or not row.get("status", "").strip():
            errors.append(f"{field}.status: expected non-empty string")

        row_keys = {str(key).strip().lower(): key for key in row}
        for jurisdiction in jurisdictions:
            key = row_keys.get(jurisdiction.lower())
            if key is None:
                errors.append(f"{field}: missing jurisdiction column {jurisdiction!r}")
                continue
            cell_value = row.get(key)
            if not isinstance(cell_value, str) or not cell_value.strip():
                errors.append(f"{field}.{key}: expected non-empty jurisdiction cell")

    return errors


def evaluate_output(output_dir: Path, case_spec: dict[str, Any] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, str] = {}

    try:
        validation_warnings = VALIDATOR.validate_output_dir(output_dir, AGENT_ID)
        warnings.extend(str(warning) for warning in validation_warnings)
        checks["output_contract"] = PASS
    except Exception as exc:
        errors.append(f"output_contract: {exc}")
        return {"status": FAIL, "errors": errors, "warnings": warnings, "checks": checks}

    structure_errors = STRUCTURE_CHECKER.check_result_structure(output_dir, AGENT_ID)
    if structure_errors:
        errors.extend(f"result_structure: {error}" for error in structure_errors)
        checks["result_structure"] = FAIL
    else:
        checks["result_structure"] = PASS

    meta_path = output_dir / f"{AGENT_ID}-meta.json"
    result_path = output_dir / f"{AGENT_ID}-result.md"
    meta = load_json(meta_path)
    result_text = result_path.read_text(encoding="utf-8")
    sources = source_by_id(meta)
    blob = text_blob(meta, result_text)
    case_spec = case_spec or {}

    issue_map = [issue for issue in meta.get("issue_map", []) if isinstance(issue, dict)]
    if not issue_map:
        errors.append("issue_map: at least one material issue is required")
    else:
        checks["issue_map_present"] = PASS

    high_confidence_c_only: list[str] = []
    high_confidence_with_limits: list[str] = []
    d_grade_citations: list[str] = []
    unsupported_issues: list[str] = []
    confidence_limits = confidence_limiting_reasons(meta)
    for issue in issue_map:
        issue_name = str(issue.get("issue", "<unnamed issue>"))
        grades = issue_authority_grades(issue, sources)
        if not grades:
            unsupported_issues.append(issue_name)
            continue
        if "D" in grades:
            d_grade_citations.append(issue_name)
        if issue.get("confidence") == "high" and not has_any_grade(grades, {"A", "B"}):
            high_confidence_c_only.append(issue_name)
        if issue.get("confidence") == "high" and confidence_limits:
            high_confidence_with_limits.append(issue_name)

    if unsupported_issues:
        errors.append(f"authority_support: issues without source support: {unsupported_issues}")
    else:
        checks["authority_support"] = PASS

    if d_grade_citations:
        errors.append(f"source_grade: D-grade source cited for legal proposition: {d_grade_citations}")
    else:
        checks["no_d_grade_legal_basis"] = PASS

    if high_confidence_c_only:
        errors.append(
            "source_grade: high-confidence issues require at least one Grade A/B source: "
            f"{high_confidence_c_only}"
        )
    else:
        checks["high_confidence_has_primary_or_official_support"] = PASS

    if high_confidence_with_limits:
        errors.append(
            "confidence_alignment: high-confidence issues are not allowed when "
            f"{', '.join(confidence_limits)}: {high_confidence_with_limits}"
        )
        checks["confidence_alignment"] = FAIL
    else:
        checks["confidence_alignment"] = PASS

    core_material_error = False
    if meta.get("error") is None and meta.get("research_mode") != "fallback":
        if not meta.get("sources"):
            errors.append("sources: non-fallback successful output must include sources")
            core_material_error = True
        if not meta.get("key_findings"):
            errors.append("key_findings: non-fallback successful output must include key findings")
            core_material_error = True
    checks["non_fallback_success_has_core_material"] = FAIL if core_material_error else PASS

    key_finding_errors = key_finding_source_errors(meta, sources)
    if key_finding_errors:
        errors.extend(key_finding_errors)
        checks["key_findings_source_support"] = FAIL
    else:
        checks["key_findings_source_support"] = PASS

    for expected in normalize_terms(case_spec.get("required_jurisdictions")):
        actual = [str(value).lower() for value in meta.get("jurisdictions", [])]
        if expected.lower() not in actual:
            errors.append(f"jurisdiction_coverage: missing required jurisdiction {expected!r}")
    if case_spec.get("required_jurisdictions"):
        checks["jurisdiction_coverage"] = PASS if not any(
            error.startswith("jurisdiction_coverage") for error in errors
        ) else FAIL

    for expected in normalize_terms(case_spec.get("required_domains")):
        actual = [str(value).lower() for value in meta.get("domains", [])]
        if expected.lower() not in actual:
            errors.append(f"domain_coverage: missing required domain {expected!r}")
    if case_spec.get("required_domains"):
        checks["domain_coverage"] = PASS if not any(error.startswith("domain_coverage") for error in errors) else FAIL

    expected_mode = case_spec.get("expected_research_mode")
    if expected_mode and meta.get("research_mode") != expected_mode:
        errors.append(
            f"research_mode: expected {expected_mode!r}, got {meta.get('research_mode')!r}"
        )
    if expected_mode:
        checks["research_mode"] = PASS if not any(error.startswith("research_mode") for error in errors) else FAIL

    expected_mode_source = case_spec.get("expected_mode_source")
    if expected_mode_source and meta.get("mode_source") != expected_mode_source:
        errors.append(
            f"mode_source: expected {expected_mode_source!r}, got {meta.get('mode_source')!r}"
        )
    if expected_mode_source:
        checks["mode_source"] = PASS if not any(error.startswith("mode_source") for error in errors) else FAIL

    expected_error = case_spec.get("expected_error")
    if "expected_error" in case_spec and meta.get("error") != expected_error:
        errors.append(f"error: expected {expected_error!r}, got {meta.get('error')!r}")
    if "expected_error" in case_spec:
        checks["error"] = PASS if not any(error.startswith("error") for error in errors) else FAIL

    expected_fallback_reason = case_spec.get("expected_fallback_reason")
    if expected_fallback_reason and meta.get("fallback_reason") != expected_fallback_reason:
        errors.append(
            "fallback_reason: expected "
            f"{expected_fallback_reason!r}, got {meta.get('fallback_reason')!r}"
        )
    if expected_fallback_reason:
        checks["fallback_reason"] = PASS if not any(
            error.startswith("fallback_reason") for error in errors
        ) else FAIL

    for expected in normalize_terms(case_spec.get("required_classification_warnings")):
        actual = [str(value).lower() for value in meta.get("classification_warnings", [])]
        if expected.lower() not in actual:
            errors.append(f"classification_warnings: missing required warning {expected!r}")
    if case_spec.get("required_classification_warnings"):
        checks["classification_warnings"] = PASS if not any(
            error.startswith("classification_warnings") for error in errors
        ) else FAIL

    for expected in normalize_terms(case_spec.get("required_coverage_gap_types")):
        if expected.lower() not in coverage_gap_types(meta):
            errors.append(f"coverage_gaps: missing required gap type {expected!r}")
    if case_spec.get("required_coverage_gap_types"):
        checks["coverage_gaps"] = PASS if not any(
            error.startswith("coverage_gaps") for error in errors
        ) else FAIL

    for taxonomy in normalize_terms(case_spec.get("required_taxonomy")):
        if taxonomy not in blob:
            errors.append(f"taxonomy_coverage: missing required taxonomy {taxonomy!r}")
    if case_spec.get("required_taxonomy"):
        checks["taxonomy_coverage"] = PASS if not any(
            error.startswith("taxonomy_coverage") for error in errors
        ) else FAIL

    for term in normalize_terms(case_spec.get("required_issue_terms")):
        if term not in blob:
            errors.append(f"material_issue_terms: missing required term {term!r}")
    if case_spec.get("required_issue_terms"):
        checks["material_issue_terms"] = PASS if not any(
            error.startswith("material_issue_terms") for error in errors
        ) else FAIL

    for term in normalize_terms(case_spec.get("required_result_terms")):
        if term not in blob:
            errors.append(f"result_terms: missing required term {term!r}")
    if case_spec.get("required_result_terms"):
        checks["result_terms"] = PASS if not any(error.startswith("result_terms") for error in errors) else FAIL

    required_source_grades = set(normalize_terms(case_spec.get("required_source_grades")))
    if required_source_grades:
        actual_grades = {str(source.get("grade", "")).lower() for source in sources.values()}
        missing_grades = sorted(required_source_grades - actual_grades)
        if missing_grades:
            errors.append(f"source_grades: missing required grades {missing_grades}")
        checks["source_grades"] = PASS if not any(error.startswith("source_grades") for error in errors) else FAIL

    for expected in normalize_terms(case_spec.get("required_co_running_agents")):
        actual = [str(value).lower() for value in meta.get("co_running_agents", [])]
        if expected.lower() not in actual:
            errors.append(f"co_running_agents: missing required co-running agent {expected!r}")
    if case_spec.get("required_co_running_agents"):
        checks["co_running_agents"] = PASS if not any(
            error.startswith("co_running_agents") for error in errors
        ) else FAIL

    if case_spec.get("requires_comparison_matrix"):
        errors.extend(comparison_matrix_errors(meta, case_spec))
        checks["comparison_matrix"] = PASS if not any(
            error.startswith("comparison_matrix") for error in errors
        ) else FAIL

    if case_spec.get("requires_privacy_handoff"):
        if not meta.get("co_running_agents"):
            errors.append("privacy_handoff: co_running_agents must identify the specialist owner")
        if "handoff" not in blob and "delegat" not in blob:
            errors.append("privacy_handoff: output must identify specialist handoff or delegation")
        checks["privacy_handoff"] = PASS if not any(
            error.startswith("privacy_handoff") for error in errors
        ) else FAIL

    status = FAIL if errors else PASS
    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "case_id": case_spec.get("id"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--case-spec", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    args = parser.parse_args(argv)

    case_spec = load_json(args.case_spec) if args.case_spec else None
    result = evaluate_output(args.output_dir, case_spec)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Quality: {result['status'].upper()}")
        for error in result["errors"]:
            print(f"FAIL: {error}")
        for warning in result["warnings"]:
            print(f"WARN: {warning}")
        if not result["errors"]:
            print("OK: legal output quality gate passed")

    return 0 if result["status"] == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
