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


def issue_source_ids(block: str) -> set[str]:
    match = re.search(r"(?m)^-\s*Sources:\s*(.+)$", block)
    if not match:
        return set()
    return referenced_source_ids(match.group(1))


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


def validate_analysis_structure(text: str) -> list[str]:
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

    errors.extend(validate_route_context(text, meta))
    errors.extend(validate_analysis_structure(text))

    issue_count = len(re.findall(r"(?m)^### Issue\b", text))
    material_issue_count = len([issue for issue in meta.get("issue_map", []) if isinstance(issue, dict)])
    if material_issue_count and issue_count < material_issue_count:
        errors.append(
            "issue_blocks: result must include at least one '### Issue' block per material issue "
            f"({issue_count}/{material_issue_count})"
        )
    elif issue_count == 0:
        errors.append("issue_blocks: result must include at least one '### Issue' block")

    for label in ("Answer:", "Sources:", "Confidence:", "Limits:"):
        if label not in text:
            errors.append(f"issue_fields: missing {label!r} in issue blocks")

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

    blocks = issue_blocks(text)
    meta_issues = [issue for issue in meta.get("issue_map", []) if isinstance(issue, dict)]
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
