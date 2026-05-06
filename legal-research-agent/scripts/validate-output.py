#!/usr/bin/env python3
"""Validate legal-research-agent output files.

This validator intentionally works without third-party dependencies. If a JSON
schema path is provided and the optional jsonschema package is installed, it also
runs schema validation.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


AGENT_ID = "legal-research-agent"
SUMMARY_MAX_ROUGH_TOKENS = 500
PLACEHOLDER_TEXT_VALUES = {"-", "none", "none.", "n/a", "na", "tbd", "to be determined"}

REQUIRED_KEYS = {
    "meta_version",
    "summary",
    "research_mode",
    "mode_source",
    "active_profile",
    "orchestrator_route_mode",
    "fallback_reason",
    "classification_warnings",
    "co_running_agents",
    "jurisdictions",
    "domains",
    "issue_map",
    "key_findings",
    "sources",
    "comparison_matrix",
    "coverage_gaps",
    "error",
}

RESEARCH_MODES = {"general", "game_regulation", "game_plus_general", "fallback"}
MODE_SOURCES = {"orchestrator", "self_classified"}
SOURCE_GRADES = {"A", "B", "C", "D"}
CONFIDENCE_VALUES = {"high", "medium", "low"}
CLAIM_SUPPORT_STRENGTHS = {"direct", "indirect", "background", "unsupported"}
CURRENTNESS_STATUSES = {
    "checked_current",
    "effective_date_checked",
    "pending_change",
    "stale_or_superseded",
    "not_checked",
    "not_applicable",
}
CURRENTNESS_CHECKED_STATUSES = {"checked_current", "effective_date_checked"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ERROR_VALUES = {
    None,
    "mcp_unavailable",
    "partial_sources",
    "timeout",
    "classification_ambiguous",
    "classification_mismatch",
    "source_coverage_insufficient",
    "internal_error",
}
GAP_TYPES = {
    "classification_mismatch",
    "source_coverage",
    "source_access",
    "jurisdiction",
    "specialist_handoff",
    "temporal_status",
    "claim_verification",
    "other",
}
ERROR_TO_GAP_TYPE = {
    "classification_mismatch": "classification_mismatch",
    "source_coverage_insufficient": "source_coverage",
    "mcp_unavailable": "source_access",
    "partial_sources": "source_access",
    "timeout": "source_access",
    "classification_ambiguous": "classification_mismatch",
}


class ValidationError(Exception):
    """Raised when output validation fails."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc


def require_type(value: Any, expected_type: type, field: str) -> None:
    if not isinstance(value, expected_type):
        raise ValidationError(f"{field}: expected {expected_type.__name__}")


def require_non_empty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field}: expected non-empty string")
    return value


def rough_token_count(value: str) -> int:
    return math.ceil(len(value) / 4)


def validate_summary(value: Any) -> None:
    summary = require_non_empty_string(value, "summary")
    if summary.strip().lower() in PLACEHOLDER_TEXT_VALUES:
        raise ValidationError("summary: expected substantive text, not a placeholder")
    rough_tokens = rough_token_count(summary)
    if rough_tokens > SUMMARY_MAX_ROUGH_TOKENS:
        raise ValidationError(
            f"summary: exceeds {SUMMARY_MAX_ROUGH_TOKENS} rough-token limit ({rough_tokens})"
        )


def validate_string_list(value: Any, field: str, require_non_empty: bool = False) -> None:
    require_type(value, list, field)
    if require_non_empty and not value:
        raise ValidationError(f"{field}: expected non-empty list")
    for index, item in enumerate(value):
        require_non_empty_string(item, f"{field}[{index}]")


def validate_date_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not DATE_PATTERN.fullmatch(value):
        raise ValidationError(f"{field}: expected YYYY-MM-DD string")


def validate_optional_date_string(value: Any, field: str) -> None:
    if value is None:
        return
    validate_date_string(value, field)


def validate_currentness(value: Any, field: str) -> None:
    require_type(value, dict, field)
    status = value.get("status")
    if status not in CURRENTNESS_STATUSES:
        raise ValidationError(f"{field}.status: invalid value {status!r}")

    checked_as_of = value.get("checked_as_of")
    if status in CURRENTNESS_CHECKED_STATUSES:
        validate_date_string(checked_as_of, f"{field}.checked_as_of")
    elif checked_as_of is not None:
        validate_optional_date_string(checked_as_of, f"{field}.checked_as_of")

    if "effective_date" in value:
        validate_optional_date_string(value.get("effective_date"), f"{field}.effective_date")

    if "notes" in value and value["notes"] is not None and not isinstance(value["notes"], str):
        raise ValidationError(f"{field}.notes: expected string or null")


def validate_sources(meta: dict[str, Any]) -> set[str]:
    sources = meta["sources"]
    require_type(sources, list, "sources")

    ids: set[str] = set()
    for index, source in enumerate(sources):
        field = f"sources[{index}]"
        require_type(source, dict, field)
        for key in ("id", "title", "grade", "citation", "pinpoint", "url_or_access"):
            if key not in source:
                raise ValidationError(f"{field}: missing {key}")
            if key != "grade" and (not isinstance(source[key], str) or not source[key].strip()):
                raise ValidationError(f"{field}.{key}: expected non-empty string")
        source_id = source["id"]
        if not isinstance(source_id, str) or not source_id:
            raise ValidationError(f"{field}.id: expected non-empty string")
        if source_id in ids:
            raise ValidationError(f"{field}.id: duplicate source id {source_id}")
        ids.add(source_id)
        if source["grade"] not in SOURCE_GRADES:
            raise ValidationError(f"{field}.grade: invalid grade {source['grade']!r}")
        if "currentness" in source:
            validate_currentness(source["currentness"], f"{field}.currentness")
    return ids


def validate_issue_map(meta: dict[str, Any], source_ids: set[str]) -> None:
    issue_map = meta["issue_map"]
    require_type(issue_map, list, "issue_map")

    for index, issue in enumerate(issue_map):
        field = f"issue_map[{index}]"
        require_type(issue, dict, field)
        for key in ("issue", "answer", "authority_ids", "confidence"):
            if key not in issue:
                raise ValidationError(f"{field}: missing {key}")
        require_non_empty_string(issue["issue"], f"{field}.issue")
        require_non_empty_string(issue["answer"], f"{field}.answer")
        require_type(issue["authority_ids"], list, f"{field}.authority_ids")
        for authority_index, source_id in enumerate(issue["authority_ids"]):
            require_non_empty_string(source_id, f"{field}.authority_ids[{authority_index}]")
        missing = [source_id for source_id in issue["authority_ids"] if source_id not in source_ids]
        if missing:
            raise ValidationError(f"{field}.authority_ids: unknown source ids {missing}")
        if issue["confidence"] not in CONFIDENCE_VALUES:
            raise ValidationError(f"{field}.confidence: invalid value {issue['confidence']!r}")


def validate_claim_checks(meta: dict[str, Any], source_ids: set[str]) -> None:
    if "claim_checks" not in meta:
        return

    claim_checks = meta["claim_checks"]
    require_type(claim_checks, list, "claim_checks")
    seen_claim_ids: set[str] = set()
    for index, claim_check in enumerate(claim_checks):
        field = f"claim_checks[{index}]"
        require_type(claim_check, dict, field)
        for key in (
            "claim_id",
            "issue_id",
            "claim",
            "authority_ids",
            "support_strength",
            "currentness",
            "confidence_impact",
            "limitation",
        ):
            if key not in claim_check:
                raise ValidationError(f"{field}: missing {key}")

        claim_id = require_non_empty_string(claim_check["claim_id"], f"{field}.claim_id")
        if claim_id in seen_claim_ids:
            raise ValidationError(f"{field}.claim_id: duplicate claim id {claim_id}")
        seen_claim_ids.add(claim_id)

        require_non_empty_string(claim_check["issue_id"], f"{field}.issue_id")
        require_non_empty_string(claim_check["claim"], f"{field}.claim")
        require_non_empty_string(claim_check["currentness"], f"{field}.currentness")
        require_non_empty_string(claim_check["confidence_impact"], f"{field}.confidence_impact")
        require_non_empty_string(claim_check["limitation"], f"{field}.limitation")

        support_strength = claim_check["support_strength"]
        if support_strength not in CLAIM_SUPPORT_STRENGTHS:
            raise ValidationError(f"{field}.support_strength: invalid value {support_strength!r}")

        require_type(claim_check["authority_ids"], list, f"{field}.authority_ids")
        if not claim_check["authority_ids"]:
            raise ValidationError(f"{field}.authority_ids: expected non-empty list")
        for authority_index, source_id in enumerate(claim_check["authority_ids"]):
            require_non_empty_string(source_id, f"{field}.authority_ids[{authority_index}]")
        missing = [source_id for source_id in claim_check["authority_ids"] if source_id not in source_ids]
        if missing:
            raise ValidationError(f"{field}.authority_ids: unknown source ids {missing}")


def validate_coverage_gaps(meta: dict[str, Any]) -> None:
    coverage_gaps = meta["coverage_gaps"]
    require_type(coverage_gaps, list, "coverage_gaps")
    for index, gap in enumerate(coverage_gaps):
        field = f"coverage_gaps[{index}]"
        require_type(gap, dict, field)
        for key in ("type", "description"):
            if key not in gap:
                raise ValidationError(f"{field}: missing {key}")
        if gap["type"] not in GAP_TYPES:
            raise ValidationError(f"{field}.type: invalid value {gap['type']!r}")
        if not isinstance(gap["description"], str) or not gap["description"].strip():
            raise ValidationError(f"{field}.description: expected non-empty string")

    required_gap_type = ERROR_TO_GAP_TYPE.get(meta["error"])
    if required_gap_type and not any(gap.get("type") == required_gap_type for gap in coverage_gaps):
        raise ValidationError(
            f"coverage_gaps: error {meta['error']!r} requires gap type {required_gap_type!r}"
        )

    if meta["research_mode"] == "fallback" and not coverage_gaps:
        raise ValidationError("coverage_gaps: required when research_mode is fallback")


def validate_meta(meta: dict[str, Any]) -> None:
    missing_keys = sorted(REQUIRED_KEYS - set(meta))
    if missing_keys:
        raise ValidationError(f"metadata missing required keys: {missing_keys}")

    validate_summary(meta["summary"])
    if meta["research_mode"] not in RESEARCH_MODES:
        raise ValidationError(f"research_mode: invalid value {meta['research_mode']!r}")
    if meta["mode_source"] not in MODE_SOURCES:
        raise ValidationError(f"mode_source: invalid value {meta['mode_source']!r}")
    if meta["error"] not in ERROR_VALUES:
        raise ValidationError(f"error: invalid value {meta['error']!r}")

    for key in ("meta_version", "active_profile", "orchestrator_route_mode"):
        require_non_empty_string(meta[key], key)

    if meta["fallback_reason"] is not None:
        require_non_empty_string(meta["fallback_reason"], "fallback_reason")

    validate_string_list(meta["classification_warnings"], "classification_warnings")
    validate_string_list(meta["co_running_agents"], "co_running_agents")
    validate_string_list(meta["jurisdictions"], "jurisdictions", require_non_empty=True)
    validate_string_list(meta["domains"], "domains", require_non_empty=True)
    validate_string_list(meta["key_findings"], "key_findings")
    require_type(meta["comparison_matrix"], list, "comparison_matrix")

    if meta["research_mode"] == "fallback" and not meta["fallback_reason"]:
        raise ValidationError("fallback_reason: required when research_mode is fallback")

    if (
        meta["error"] == "classification_mismatch"
        and "classification_mismatch" not in meta["classification_warnings"]
    ):
        raise ValidationError(
            "classification_warnings: must include classification_mismatch when error uses it"
        )

    source_ids = validate_sources(meta)
    validate_issue_map(meta, source_ids)
    validate_claim_checks(meta, source_ids)
    validate_coverage_gaps(meta)


def validate_schema(meta: dict[str, Any], schema_path: Path) -> list[str]:
    if not schema_path.exists():
        raise ValidationError(f"schema path does not exist: {schema_path}")
    try:
        import jsonschema  # type: ignore[import-not-found]
    except ImportError:
        return ["jsonschema package not installed; skipped schema validation"]

    schema = load_json(schema_path)
    jsonschema.validate(meta, schema)
    return []


def validate_output_dir(output_dir: Path, agent_id: str, schema_path: Path | None = None) -> list[str]:
    result_path = output_dir / f"{agent_id}-result.md"
    meta_path = output_dir / f"{agent_id}-meta.json"

    if not result_path.exists():
        raise ValidationError(f"missing result file: {result_path}")
    if not meta_path.exists():
        raise ValidationError(f"missing metadata file: {meta_path}")
    if not result_path.read_text(encoding="utf-8").strip():
        raise ValidationError(f"empty result file: {result_path}")

    meta = load_json(meta_path)
    require_type(meta, dict, "metadata")
    validate_meta(meta)

    warnings: list[str] = []
    if schema_path:
        warnings.extend(validate_schema(meta, schema_path))
    return warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--agent-id", default=AGENT_ID)
    parser.add_argument("--schema", type=Path)
    args = parser.parse_args(argv)

    try:
        warnings = validate_output_dir(args.output_dir, args.agent_id, args.schema)
    except ValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"FAIL: unexpected validation error: {exc}", file=sys.stderr)
        return 1

    print("OK: output contract valid")
    for warning in warnings:
        print(f"WARN: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
