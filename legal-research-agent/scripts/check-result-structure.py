#!/usr/bin/env python3
"""Check that legal-research-agent result markdown has a usable memo structure."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


AGENT_ID = "legal-research-agent"
REQUIRED_HEADINGS = [
    "# Legal Research Result",
    "## Question",
    "## Route Context",
    "## Short Answer",
    "## Issues",
    "## Analysis",
    "## Sources",
    "## Coverage Gaps",
    "## Handoff Notes",
]
REQUIRED_ANALYSIS_HEADINGS = [
    "### Rule And Authority",
    "### Application",
    "### Counter-Analysis Or Caveat",
    "### Practical Next Step",
]
SOURCE_TABLE_HEADER = "| ID | Grade | Title | Citation | Pinpoint |"
PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}]+\}\}")
ROUTE_CONTEXT_LABELS = {
    "Active profile": "active_profile",
    "Orchestrator route mode": "orchestrator_route_mode",
    "Research mode": "research_mode",
    "Mode source": "mode_source",
}
REQUIRED_ISSUE_FIELDS = ("Answer", "Sources", "Confidence", "Limits")
GAME_RESEARCH_MODES = {"game_regulation", "game_plus_general"}
EMPTY_FIELD_VALUES = {"", "-", "none", "none.", "n/a", "na", "tbd", "to be determined"}
EMPTY_SECTION_VALUES = EMPTY_FIELD_VALUES | {"not specified", "unspecified"}
LIMITING_SHORT_ANSWER_TERMS = (
    "cannot",
    "conservative",
    "fallback",
    "gap",
    "insufficient",
    "source-limited",
    "source limited",
    "unverified",
    "verify",
)
HANDOFF_TERMS = ("handoff", "delegat")


class StructureError(Exception):
    """Raised when result markdown structure is insufficient."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise StructureError(f"{path}: invalid JSON: {exc}") from exc


def source_ids(meta: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for source in meta.get("sources", []):
        if isinstance(source, dict) and isinstance(source.get("id"), str):
            ids.add(source["id"])
    return ids


def source_grades(meta: dict[str, Any]) -> dict[str, str]:
    grades: dict[str, str] = {}
    for source in meta.get("sources", []):
        if isinstance(source, dict) and isinstance(source.get("id"), str):
            grades[source["id"]] = str(source.get("grade", ""))
    return grades


def heading_positions(text: str) -> dict[str, int]:
    positions: dict[str, int] = {}
    for heading in REQUIRED_HEADINGS:
        match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
        if match:
            positions[heading] = match.start()
    return positions


def referenced_source_ids(text: str) -> set[str]:
    return set(re.findall(r"\bsrc_[0-9A-Za-z_-]+\b", text))


def section_text(text: str, heading: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(heading)}\s*(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def normalize_display_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def route_context_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    context = section_text(text, "## Route Context")
    for line in context.splitlines():
        match = re.match(r"^-\s*([^:]+):\s*(.+?)\s*$", line)
        if not match:
            continue
        label = match.group(1).strip()
        value = match.group(2).strip().strip("`").strip()
        values[label] = value
    return values


def normalize_agent_list(value: str) -> list[str]:
    value = value.strip().strip("`").strip()
    if value in {"", "[]"}:
        return []
    value = value.strip("[]").strip()
    if not value:
        return []
    return [item.strip().strip("`").strip() for item in value.split(",") if item.strip()]


def source_table_text(text: str) -> str:
    match = re.search(r"(?ms)^## Sources\s*(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def source_table_rows(text: str) -> tuple[dict[str, dict[str, str]], list[str]]:
    rows: dict[str, dict[str, str]] = {}
    errors: list[str] = []
    for line in source_table_text(text).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or not re.fullmatch(r"src_[0-9A-Za-z_-]+", cells[0]):
            continue

        source_id, grade, title, citation, pinpoint = cells[:5]
        if source_id in rows:
            errors.append(f"sources_table: duplicate row for source id {source_id!r}")
        row = {
            "grade": grade,
            "title": title,
            "citation": citation,
            "pinpoint": pinpoint,
        }
        for field, value in row.items():
            if not value:
                errors.append(f"sources_table: {source_id}.{field} is empty")
        rows[source_id] = row
    return rows, errors


def issue_blocks(text: str) -> list[str]:
    matches = list(re.finditer(r"(?m)^### Issue\b.*$", text))
    blocks: list[str] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        blocks.append(text[start:end])
    return blocks


def issue_field_value(block: str, field: str) -> str | None:
    match = re.search(rf"(?m)^-[ \t]*{re.escape(field)}:[ \t]*(.*)$", block)
    if not match:
        return None
    return match.group(1).strip()


def is_meaningful_issue_value(value: str | None) -> bool:
    if value is None:
        return False
    normalized = value.strip().lower()
    return normalized not in EMPTY_FIELD_VALUES


def normalize_issue_value(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip().strip("`").strip().lower()


def issue_source_ids(block: str) -> set[str]:
    value = issue_field_value(block, "Sources")
    if value is None:
        return set()
    return referenced_source_ids(value)


def validate_issue_blocks(blocks: list[str], meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    meta_issues = [issue for issue in meta.get("issue_map", []) if isinstance(issue, dict)]
    research_mode = str(meta.get("research_mode", ""))
    required_fields = list(REQUIRED_ISSUE_FIELDS)
    if research_mode in GAME_RESEARCH_MODES:
        required_fields.append("Taxonomy")

    for block_index, block in enumerate(blocks):
        issue_number = block_index + 1
        for field in required_fields:
            value = issue_field_value(block, field)
            if value is None:
                errors.append(f"issue_blocks: issue {issue_number} missing field {field!r}")
                continue
            if not is_meaningful_issue_value(value):
                errors.append(f"issue_blocks: issue {issue_number} empty field {field!r}")

        if issue_field_value(block, "Sources") is not None and not issue_source_ids(block):
            errors.append(f"issue_blocks: issue {issue_number} Sources field has no source ids")

    for index, issue in enumerate(meta_issues):
        if index >= len(blocks):
            continue
        expected_ids = {str(source_id) for source_id in issue.get("authority_ids", []) if str(source_id)}
        displayed_ids = issue_source_ids(blocks[index])
        missing_issue_sources = sorted(expected_ids - displayed_ids)
        if missing_issue_sources:
            errors.append(
                f"issue_blocks: issue {index + 1} missing authority source ids {missing_issue_sources}"
            )

        expected_confidence = normalize_issue_value(str(issue.get("confidence", "")))
        displayed_confidence = normalize_issue_value(issue_field_value(blocks[index], "Confidence"))
        if expected_confidence and displayed_confidence and expected_confidence != displayed_confidence:
            errors.append(
                "issue_blocks: issue "
                f"{index + 1} confidence mismatch result={displayed_confidence!r} "
                f"metadata={expected_confidence!r}"
            )

    return errors


def validate_route_context(text: str, meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    context = route_context_values(text)
    for label, meta_key in ROUTE_CONTEXT_LABELS.items():
        if label not in context:
            errors.append(f"route_context: missing {label!r}")
            continue
        expected = str(meta.get(meta_key, ""))
        if context[label] != expected:
            errors.append(
                f"route_context: {label} mismatch result={context[label]!r} metadata={expected!r}"
            )

    if "Co-running agents" not in context:
        errors.append("route_context: missing 'Co-running agents'")
    else:
        displayed_agents = normalize_agent_list(context["Co-running agents"])
        expected_agents = [str(agent) for agent in meta.get("co_running_agents", [])]
        if displayed_agents != expected_agents:
            errors.append(
                "route_context: Co-running agents mismatch "
                f"result={displayed_agents!r} metadata={expected_agents!r}"
            )
    return errors


def validate_question(text: str) -> list[str]:
    question = section_text(text, "## Question").strip()
    if not question:
        return ["question: section must not be empty"]
    if question.lower() in EMPTY_SECTION_VALUES:
        return ["question: section must contain the actual user question"]
    if len(question) < 8:
        return ["question: section is too short to preserve the user question"]
    return []


def analysis_subsection_positions(analysis: str) -> dict[str, int]:
    positions: dict[str, int] = {}
    for heading in REQUIRED_ANALYSIS_HEADINGS:
        match = re.search(rf"(?m)^{re.escape(heading)}\s*$", analysis)
        if match:
            positions[heading] = match.start()
    return positions


def analysis_subsection_body(analysis: str, heading: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(heading)}\s*(.*?)(?=^### |\Z)", analysis)
    return match.group(1).strip() if match else ""


def authority_ids_from_issues(meta: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for issue in meta.get("issue_map", []):
        if not isinstance(issue, dict):
            continue
        for source_id in issue.get("authority_ids", []):
            normalized = str(source_id).strip()
            if normalized:
                ids.add(normalized)
    return ids


def validate_analysis_structure(text: str, meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    analysis = section_text(text, "## Analysis")
    positions = analysis_subsection_positions(analysis)

    for heading in REQUIRED_ANALYSIS_HEADINGS:
        if heading not in positions:
            errors.append(f"analysis_structure: missing required analysis subsection {heading!r}")
            continue
        if not analysis_subsection_body(analysis, heading):
            errors.append(f"analysis_structure: empty analysis subsection {heading!r}")

    ordered_positions = [positions[heading] for heading in REQUIRED_ANALYSIS_HEADINGS if heading in positions]
    if ordered_positions != sorted(ordered_positions):
        errors.append("analysis_structure: required analysis subsections are out of order")

    rule_body = analysis_subsection_body(analysis, "### Rule And Authority")
    displayed_rule_ids = referenced_source_ids(rule_body)
    expected_rule_ids = authority_ids_from_issues(meta)
    known_source_ids = source_ids(meta)
    if known_source_ids and not (displayed_rule_ids & known_source_ids):
        errors.append("analysis_structure: Rule And Authority must cite at least one metadata source id")
    missing_rule_ids = sorted(expected_rule_ids - displayed_rule_ids)
    if missing_rule_ids:
        errors.append(
            f"analysis_structure: Rule And Authority missing authority source ids {missing_rule_ids}"
        )

    return errors


def validate_short_answer(text: str, meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    short_answer = section_text(text, "## Short Answer").strip()
    if not short_answer:
        return ["short_answer: section must not be empty"]

    normalized = short_answer.lower()
    if re.fullmatch(r"(?is)\s*(none|none\.|n/a|tbd|to be determined)\s*", short_answer):
        errors.append("short_answer: section must contain a substantive answer")

    known_source_ids = source_ids(meta)
    if known_source_ids and not (referenced_source_ids(short_answer) & known_source_ids):
        errors.append("short_answer: must cite at least one metadata source id")

    has_structured_gap = any(isinstance(gap, dict) for gap in meta.get("coverage_gaps", []))
    needs_limiting_language = (
        has_structured_gap
        or meta.get("error") is not None
        or str(meta.get("research_mode", "")) == "fallback"
    )
    if needs_limiting_language and not any(term in normalized for term in LIMITING_SHORT_ANSWER_TERMS):
        errors.append("short_answer: fallback, error, or coverage-gap output needs visible limiting language")

    co_running_agents = [str(agent).strip() for agent in meta.get("co_running_agents", []) if str(agent).strip()]
    if co_running_agents:
        if not any(term in normalized for term in HANDOFF_TERMS):
            errors.append("short_answer: co-running agents require visible handoff or delegation language")
        for agent in co_running_agents:
            if agent.lower() not in normalized:
                errors.append(f"short_answer: missing co-running agent {agent!r}")

    return errors


def validate_coverage_gap_display(text: str, meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    coverage = section_text(text, "## Coverage Gaps").strip()
    if not coverage:
        return ["coverage_gaps: section must not be empty"]

    metadata_gaps = [gap for gap in meta.get("coverage_gaps", []) if isinstance(gap, dict)]
    if not metadata_gaps:
        return errors

    normalized_coverage = coverage.lower().replace("_", " ")
    if re.fullmatch(r"(?is)\s*(none|none\.|none identified\.?|n/a)\s*", coverage):
        errors.append("coverage_gaps: metadata gaps exist but result says none")

    for index, gap in enumerate(metadata_gaps):
        gap_type = str(gap.get("type", "")).strip()
        if not gap_type:
            continue
        terms = [term for term in gap_type.lower().replace("_", " ").split() if term]
        missing_terms = [term for term in terms if term not in normalized_coverage]
        if missing_terms:
            errors.append(
                f"coverage_gaps: gap {index + 1} type {gap_type!r} not displayed in result"
            )

    return errors


def validate_handoff_notes_display(text: str, meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    handoff = section_text(text, "## Handoff Notes").strip()
    if not handoff:
        return ["handoff_notes: section must not be empty"]

    co_running_agents = [str(agent).strip() for agent in meta.get("co_running_agents", []) if str(agent).strip()]
    if not co_running_agents:
        return errors

    normalized_handoff = handoff.lower()
    if re.fullmatch(r"(?is)\s*(none|none\.|n/a)\s*", handoff):
        errors.append("handoff_notes: co-running agents exist but result says none")

    if "handoff" not in normalized_handoff and "delegat" not in normalized_handoff:
        errors.append("handoff_notes: co-running agents require visible handoff or delegation language")

    for agent in co_running_agents:
        if agent.lower() not in normalized_handoff:
            errors.append(f"handoff_notes: missing co-running agent {agent!r}")

    return errors


def validate_comparison_matrix_display(text: str, meta: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    matrix = [row for row in meta.get("comparison_matrix", []) if isinstance(row, dict)]
    if not matrix:
        return errors

    section = section_text(text, "## Comparison Matrix").strip()
    if not section:
        return ["comparison_matrix_display: metadata comparison_matrix exists but section is missing"]

    normalized_section = normalize_display_text(section)
    table_lines = [line for line in section.splitlines() if line.strip().startswith("|")]
    if not table_lines:
        errors.append("comparison_matrix_display: section must include a markdown table")

    for label in ("issue", "status"):
        if label not in normalized_section:
            errors.append(f"comparison_matrix_display: table header missing {label!r}")

    jurisdictions = [str(value).strip() for value in meta.get("jurisdictions", []) if str(value).strip()]
    for jurisdiction in jurisdictions:
        if normalize_display_text(jurisdiction) not in normalized_section:
            errors.append(f"comparison_matrix_display: table header missing jurisdiction {jurisdiction!r}")

    for index, row in enumerate(matrix):
        field = f"comparison_matrix[{index}]"
        issue = str(row.get("issue", "")).strip()
        status = str(row.get("status", "")).strip()
        if issue and normalize_display_text(issue) not in normalized_section:
            errors.append(f"comparison_matrix_display: missing {field}.issue {issue!r}")
        if status and normalize_display_text(status) not in normalized_section:
            errors.append(f"comparison_matrix_display: missing {field}.status {status!r}")

        row_keys = {str(key).strip().lower(): key for key in row}
        for jurisdiction in jurisdictions:
            key = row_keys.get(jurisdiction.lower())
            if key is None:
                continue
            cell_value = str(row.get(key, "")).strip()
            if cell_value and normalize_display_text(cell_value) not in normalized_section:
                errors.append(
                    f"comparison_matrix_display: missing {field}.{key} cell {cell_value!r}"
                )

    return errors


def check_result_structure(output_dir: Path, agent_id: str = AGENT_ID) -> list[str]:
    result_path = output_dir / f"{agent_id}-result.md"
    meta_path = output_dir / f"{agent_id}-meta.json"
    errors: list[str] = []

    if not result_path.exists():
        return [f"missing result file: {result_path}"]
    if not meta_path.exists():
        return [f"missing metadata file: {meta_path}"]

    text = result_path.read_text(encoding="utf-8")
    meta = load_json(meta_path)
    if not isinstance(meta, dict):
        return ["metadata: expected object"]

    if PLACEHOLDER_PATTERN.search(text):
        errors.append("placeholders: unresolved template placeholder found")

    positions = heading_positions(text)
    for heading in REQUIRED_HEADINGS:
        if heading not in positions:
            errors.append(f"heading: missing required heading {heading!r}")

    ordered_positions = [positions[heading] for heading in REQUIRED_HEADINGS if heading in positions]
    if ordered_positions != sorted(ordered_positions):
        errors.append("heading_order: required headings are out of order")

    errors.extend(validate_question(text))
    errors.extend(validate_route_context(text, meta))
    errors.extend(validate_short_answer(text, meta))
    errors.extend(validate_analysis_structure(text, meta))
    errors.extend(validate_comparison_matrix_display(text, meta))
    errors.extend(validate_coverage_gap_display(text, meta))
    errors.extend(validate_handoff_notes_display(text, meta))

    issue_count = len(re.findall(r"(?m)^### Issue\b", text))
    material_issue_count = len([issue for issue in meta.get("issue_map", []) if isinstance(issue, dict)])
    if material_issue_count and issue_count < material_issue_count:
        errors.append(
            "issue_blocks: result must include at least one '### Issue' block per material issue "
            f"({issue_count}/{material_issue_count})"
        )
    elif issue_count == 0:
        errors.append("issue_blocks: result must include at least one '### Issue' block")

    if SOURCE_TABLE_HEADER not in text:
        errors.append("sources_table: missing required source table header")

    known_source_ids = source_ids(meta)
    known_source_grades = source_grades(meta)
    used_source_ids = referenced_source_ids(text)
    unknown_source_ids = sorted(used_source_ids - known_source_ids)
    if unknown_source_ids:
        errors.append(f"sources: result references unknown source ids {unknown_source_ids}")

    if known_source_ids and not (used_source_ids & known_source_ids):
        errors.append("sources: result does not reference any metadata source id")

    table_rows, table_row_errors = source_table_rows(text)
    errors.extend(table_row_errors)
    missing_table_sources = sorted(known_source_ids - set(table_rows))
    if missing_table_sources:
        errors.append(f"sources_table: missing metadata source rows {missing_table_sources}")

    extra_table_sources = sorted(set(table_rows) - known_source_ids)
    if extra_table_sources:
        errors.append(f"sources_table: table includes unknown source rows {extra_table_sources}")

    grade_mismatches = sorted(
        f"{source_id}: metadata={known_source_grades[source_id]!r} table={table_rows[source_id]['grade']!r}"
        for source_id in known_source_ids & set(table_rows)
        if known_source_grades[source_id] != table_rows[source_id]["grade"]
    )
    if grade_mismatches:
        errors.append(f"sources_table: grade mismatch {grade_mismatches}")

    detail_mismatches: list[str] = []
    for source in meta.get("sources", []):
        if not isinstance(source, dict) or not isinstance(source.get("id"), str):
            continue
        source_id = source["id"]
        if source_id not in table_rows:
            continue
        for field in ("title", "citation", "pinpoint"):
            metadata_value = str(source.get(field, ""))
            table_value = table_rows[source_id][field]
            if metadata_value != table_value:
                detail_mismatches.append(
                    f"{source_id}.{field}: metadata={metadata_value!r} table={table_value!r}"
                )
    if detail_mismatches:
        errors.append(f"sources_table: detail mismatch {sorted(detail_mismatches)}")

    errors.extend(validate_issue_blocks(issue_blocks(text), meta))

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--agent-id", default=AGENT_ID)
    args = parser.parse_args(argv)

    errors = check_result_structure(args.output_dir, args.agent_id)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: result structure valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
