#!/usr/bin/env python3
"""Validate standalone formatter markdown against research metadata."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ID_PATTERN = re.compile(r"(?<![0-9A-Za-z_])src_[0-9A-Za-z_-]+(?![0-9A-Za-z_-])")
TABLE_SOURCE_ID_PATTERN = re.compile(r"^src_[0-9A-Za-z_-]+$")

STANDALONE_HEADINGS = {
    "ko": [
        "## 요약",
        "## 쟁점",
        "## 검토의견",
        "## 분석",
        "## 한계 및 추가 확인사항",
        "## 출처",
    ],
    "en": [
        "## Executive Summary",
        "## Issues Presented",
        "## Short Answer",
        "## Analysis",
        "## Limitations and Next Steps",
        "## Sources",
    ],
}
HANDOFF_PACKET_HEADINGS = [
    "## Formatter Target",
    "## Route Context",
    "## Issues",
    "## Key Findings",
    "## Sources",
    "## Coverage Gaps",
    "## Handoff Notes",
]
SOURCE_SECTION_BY_LANGUAGE = {"ko": "## 출처", "en": "## Sources"}
LIMITS_SECTION_BY_LANGUAGE = {
    "ko": "## 한계 및 추가 확인사항",
    "en": "## Limitations and Next Steps",
}
ANCHORED_SECTIONS_BY_LANGUAGE = {
    "ko": ("## 요약", "## 검토의견", "## 분석"),
    "en": ("## Executive Summary", "## Short Answer", "## Analysis"),
}
ANCHOR_EXEMPT_TERMS = (
    "source coverage gap",
    "source-limited",
    "source limited",
    "coverage gap",
    "[source coverage gap",
    "추가 확인",
    "단정하기 어렵",
    "source-limited",
)
HANDOFF_TERMS = ("handoff", "delegate", "delegated", "인계", "위임", "별도 전문가")
FORBIDDEN_DOCX_READY_CHAT_TERMS = (
    "as an ai",
    "here is",
    "below is",
    "i can",
    "chatgpt",
)

OUTPUT_MODE_SLUGS = (
    "canonical",
    "executive_brief",
    "comparative_matrix",
    "enforcement_case_law",
    "black_letter_commentary",
)

REQUIRED_OUTPUT_MODE_SECTIONS: dict[str, list[str]] = {
    "executive_brief": [
        "## Scope and As-of Date",
        "## Key Conclusions",
        "## Counter-Analysis and Risk Assessment",
        "## Risk and Priority Ranking",
        "## Practical Implications",
        "## Immediate Action Checklist",
        "## Top Sources",
        "## Verification Guide",
    ],
    "comparative_matrix": [
        "## Scope and As-of Date",
        "## Comparative Matrix",
        "## Divergence Commentary",
        "## Counter-Analysis",
        "## Practical Implications",
        "## Annotated Bibliography",
        "## Verification Guide",
    ],
    "enforcement_case_law": [
        "## Scope and As-of Date",
        "## Conclusion Summary",
        "## Enforcement Timeline",
        "## Case and Decision Summaries",
        "## Counter-Analysis",
        "## Practical Implications",
        "## Annotated Bibliography",
        "## Verification Guide",
    ],
    "black_letter_commentary": [
        "## Scope and As-of Date",
        "## Legal System Overview",
        "## Core Definitions and Scope",
        "## Article-by-Article Commentary",
        "## Implementation Relationships",
        "## Practical Implications",
        "## Annotated Bibliography",
        "## Verification Guide",
    ],
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def source_ids(meta: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for source in meta.get("sources", []):
        if isinstance(source, dict) and isinstance(source.get("id"), str):
            ids.add(source["id"])
    return ids


def source_by_id(meta: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        source["id"]: source
        for source in meta.get("sources", [])
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }


def referenced_source_ids(text: str) -> set[str]:
    return set(SOURCE_ID_PATTERN.findall(text))


def heading_positions(text: str, headings: list[str]) -> dict[str, int]:
    positions: dict[str, int] = {}
    for heading in headings:
        match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
        if match:
            positions[heading] = match.start()
    return positions


def section_text(text: str, heading: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(heading)}\s*(.*?)(?=^## |\Z)", text)
    return match.group(1).strip() if match else ""


def readable_gap_type(gap_type: str) -> str:
    return gap_type.replace("_", " ").strip().lower()


def infer_language(path: Path) -> str:
    name = path.as_posix().lower()
    if "/ko" in name or "ko-" in name or "_ko" in name:
        return "ko"
    if "/en" in name or "en-" in name or "_en" in name:
        return "en"
    raise ValueError(f"cannot infer formatter language from path: {path}")


def required_headings(language: str, mode: str) -> list[str]:
    if mode == "handoff_packet":
        return HANDOFF_PACKET_HEADINGS
    return STANDALONE_HEADINGS[language]


def validate_title(text: str) -> list[str]:
    titles = re.findall(r"(?m)^#\s+\S.*$", text)
    if len(titles) != 1:
        return [f"title: expected exactly one H1 title, found {len(titles)}"]
    return []


def validate_headings(text: str, language: str, mode: str) -> list[str]:
    errors: list[str] = []
    headings = required_headings(language, mode)
    positions = heading_positions(text, headings)
    for heading in headings:
        if heading not in positions:
            errors.append(f"headings: missing {heading!r}")
    ordered_positions = [positions[heading] for heading in headings if heading in positions]
    if ordered_positions != sorted(ordered_positions):
        errors.append("headings: required formatter headings are out of order")
    return errors


def source_table_rows(text: str, language: str, mode: str) -> dict[str, dict[str, str]]:
    source_heading = "## Sources" if mode == "handoff_packet" else SOURCE_SECTION_BY_LANGUAGE[language]
    rows: dict[str, dict[str, str]] = {}
    for line in section_text(text, source_heading).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 6 or not TABLE_SOURCE_ID_PATTERN.fullmatch(cells[0]):
            continue
        source_id, grade, title, citation, pinpoint, access = cells[:6]
        rows[source_id] = {
            "grade": grade,
            "title": title,
            "citation": citation,
            "pinpoint": pinpoint,
            "url_or_access": access,
        }
    return rows


def validate_sources(text: str, meta: dict[str, Any], language: str, mode: str) -> list[str]:
    errors: list[str] = []
    expected_sources = source_by_id(meta)
    expected_ids = set(expected_sources)
    unknown = sorted(referenced_source_ids(text) - expected_ids)
    if unknown:
        errors.append(f"sources: unknown source ids referenced {unknown}")

    rows = source_table_rows(text, language, mode)
    missing_rows = sorted(expected_ids - set(rows))
    if missing_rows:
        errors.append(f"sources: missing source table rows {missing_rows}")

    for source_id, row in rows.items():
        if source_id not in expected_sources:
            continue
        source = expected_sources[source_id]
        for field in ("grade", "title", "citation", "pinpoint", "url_or_access"):
            expected = str(source.get(field, "")).strip()
            actual = row.get(field, "").strip()
            if not actual:
                errors.append(f"sources: {source_id}.{field} is empty")
            elif actual != expected:
                errors.append(
                    f"sources: {source_id}.{field} mismatch formatted={actual!r} metadata={expected!r}"
                )
    return errors


def material_paragraphs(section: str) -> list[str]:
    paragraphs: list[str] = []
    for paragraph in re.split(r"\n\s*\n", section):
        cleaned = paragraph.strip()
        if not cleaned:
            continue
        if cleaned.startswith("#") or cleaned.startswith("|"):
            continue
        if re.fullmatch(r"[-*]\s+.+", cleaned) and len(cleaned) < 80:
            continue
        if len(cleaned) < 80:
            continue
        paragraphs.append(cleaned)
    return paragraphs


def paragraph_has_anchor_or_gap(paragraph: str) -> bool:
    if referenced_source_ids(paragraph):
        return True
    lower = paragraph.lower()
    return any(term in lower for term in ANCHOR_EXEMPT_TERMS)


def validate_source_anchoring(text: str, language: str, mode: str) -> list[str]:
    if mode == "handoff_packet":
        return []
    errors: list[str] = []
    for heading in ANCHORED_SECTIONS_BY_LANGUAGE[language]:
        body = section_text(text, heading)
        if not body:
            continue
        for index, paragraph in enumerate(material_paragraphs(body), start=1):
            if not paragraph_has_anchor_or_gap(paragraph):
                errors.append(f"source_anchoring: {heading} paragraph {index} has no source anchor or gap marker")
    return errors


def validate_gaps_and_handoffs(text: str, meta: dict[str, Any], language: str, mode: str) -> list[str]:
    errors: list[str] = []
    if mode == "handoff_packet":
        limits_text = section_text(text, "## Coverage Gaps") + "\n" + section_text(text, "## Handoff Notes")
    else:
        limits_text = section_text(text, LIMITS_SECTION_BY_LANGUAGE[language])
    limits_lower = limits_text.lower()

    gaps = [gap for gap in meta.get("coverage_gaps", []) if isinstance(gap, dict)]
    if gaps and ("none" in limits_lower or "없음" in limits_text):
        errors.append("coverage_gaps: formatted output says none despite metadata gaps")
    for gap in gaps:
        gap_type = str(gap.get("type", "")).strip()
        if gap_type and readable_gap_type(gap_type) not in limits_lower:
            errors.append(f"coverage_gaps: missing visible gap type {gap_type!r}")

    fallback_reason = meta.get("fallback_reason")
    error_code = meta.get("error")
    if fallback_reason and str(fallback_reason).lower() not in limits_lower:
        errors.append(f"fallback: missing fallback reason {fallback_reason!r}")
    if error_code and str(error_code).lower() not in limits_lower:
        errors.append(f"error: missing error code {error_code!r}")

    co_running_agents = [str(agent) for agent in meta.get("co_running_agents", []) if str(agent)]
    if co_running_agents:
        combined_lower = text.lower()
        if not any(term in combined_lower for term in HANDOFF_TERMS):
            errors.append("handoff: missing visible handoff/delegation language")
        for agent in co_running_agents:
            if agent.lower() not in combined_lower:
                errors.append(f"handoff: missing co-running agent {agent!r}")
    return errors


def validate_docx_ready(text: str, mode: str) -> list[str]:
    if mode != "docx_ready_markdown":
        return []
    lower = text.lower()
    errors = []
    for term in FORBIDDEN_DOCX_READY_CHAT_TERMS:
        if term in lower:
            errors.append(f"docx_ready_markdown: contains chat-only term {term!r}")
    if re.search(r"(?m)^#{5,}\s+", text):
        errors.append("docx_ready_markdown: heading depth deeper than ####")
    return errors


def validate_formatter_output(
    formatted_path: Path,
    meta_path: Path,
    *,
    language: str,
    mode: str = "standalone_markdown",
) -> list[str]:
    text = formatted_path.read_text(encoding="utf-8")
    meta = load_json(meta_path)

    errors: list[str] = []
    errors.extend(validate_title(text))
    errors.extend(validate_headings(text, language, mode))
    errors.extend(validate_sources(text, meta, language, mode))
    errors.extend(validate_source_anchoring(text, language, mode))
    errors.extend(validate_gaps_and_handoffs(text, meta, language, mode))
    errors.extend(validate_docx_ready(text, mode))
    return errors


def validate_mode_shaped_deliverable(
    formatted_path: Path,
    meta_path: Path,
    *,
    output_mode: str,
) -> list[str]:
    """Validate a mode-shaped deliverable (executive_brief / comparative_matrix /
    enforcement_case_law / black_letter_commentary).

    Mode-shaped deliverables use template-specific H2 headings, not the
    canonical standalone-memo headings. This validator therefore replaces
    the standalone heading check with the per-mode required-section check,
    while still validating source-anchor parity against metadata.
    """
    if output_mode not in REQUIRED_OUTPUT_MODE_SECTIONS:
        return [
            f"{formatted_path}: unsupported output_mode {output_mode!r}; "
            f"expected one of {sorted(REQUIRED_OUTPUT_MODE_SECTIONS)}"
        ]

    text = formatted_path.read_text(encoding="utf-8")
    meta = load_json(meta_path)
    errors: list[str] = []

    errors.extend(validate_title(text))

    for section in REQUIRED_OUTPUT_MODE_SECTIONS[output_mode]:
        if section not in text:
            errors.append(
                f"{formatted_path}: missing required section for "
                f"output_mode={output_mode!r}: {section!r}"
            )

    known_ids = source_ids(meta)
    referenced = referenced_source_ids(text)
    for ref in sorted(referenced):
        if ref not in known_ids:
            errors.append(
                f"{formatted_path}: source anchor {ref!r} not present in "
                f"meta sources"
            )

    meta_output_mode = meta.get("output_mode")
    if meta_output_mode is not None and meta_output_mode != output_mode:
        errors.append(
            f"{meta_path}: meta output_mode={meta_output_mode!r} does not "
            f"match requested {output_mode!r}"
        )

    return errors


def validate_fixture_root(root: Path, mode: str | None = None) -> list[str]:
    errors: list[str] = []
    formatted_files = sorted(root.rglob("formatted.md"))
    if not formatted_files:
        return [f"formatter fixtures: no formatted.md files found under {root}"]
    for formatted_path in formatted_files:
        meta_path = formatted_path.with_name("legal-research-agent-meta.json")
        if not meta_path.exists():
            errors.append(f"{formatted_path}: missing legal-research-agent-meta.json")
            continue
        try:
            language = infer_language(formatted_path)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        selected_mode = mode or "standalone_markdown"
        fixture_errors = validate_formatter_output(
            formatted_path,
            meta_path,
            language=language,
            mode=selected_mode,
        )
        errors.extend(f"{formatted_path}: {error}" for error in fixture_errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="formatted.md file or fixture root")
    parser.add_argument("--meta", type=Path, help="metadata path when validating one file")
    parser.add_argument("--language", choices=("ko", "en"), help="formatter language for one file")
    parser.add_argument(
        "--mode",
        choices=("standalone_markdown", "handoff_packet", "docx_ready_markdown"),
        default=None,
    )
    parser.add_argument(
        "--output-mode",
        choices=OUTPUT_MODE_SLUGS,
        default=None,
        help=(
            "Optional output-mode-specific structural check. Non-canonical "
            "modes use the per-mode template required-sections instead of "
            "the canonical standalone headings."
        ),
    )
    args = parser.parse_args(argv)

    if args.path.is_dir() and args.meta is None:
        errors = validate_fixture_root(args.path, mode=args.mode)
    else:
        if args.meta is None:
            print("FAIL: --meta is required when path is a file", file=sys.stderr)
            return 1
        if args.output_mode and args.output_mode != "canonical":
            errors = validate_mode_shaped_deliverable(
                args.path, args.meta, output_mode=args.output_mode
            )
        else:
            language = args.language or infer_language(args.path)
            mode = args.mode or "standalone_markdown"
            errors = validate_formatter_output(
                args.path, args.meta, language=language, mode=mode
            )

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: formatter output valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
