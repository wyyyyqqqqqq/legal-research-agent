#!/usr/bin/env python3
"""Validate user-config.json schema when the file is present.

This validator is intentionally tolerant: if user-config.json does not
exist, the script exits 0 and prints a SKIP line. The file is
gitignored runtime state created by the /onboard wizard.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ALLOWED_INDUSTRIES = {
    "game", "fintech", "healthcare", "platform",
    "e_commerce", "media", "other",
}
ALLOWED_AREAS = {
    "general", "regulatory", "contract", "consumer_protection",
    "intellectual_property", "employment", "privacy", "tax",
    "competition", "other",
}
ALLOWED_RESEARCH_MODES = {
    "general", "game_regulation", "game_plus_general", "fallback",
}
ALLOWED_OUTPUT_MODES = {
    "canonical", "executive_brief", "comparative_matrix",
    "enforcement_case_law", "black_letter_commentary",
}
ALLOWED_PACKAGING = {
    "standalone_markdown", "handoff_packet", "docx_ready_markdown",
}
ALLOWED_LANGUAGES = {"ko", "en", "bilingual"}
ALLOWED_REVIEW_STATUSES = {"draft", "verified"}
ALLOWED_AUDIT_STATUSES = {
    "not_required", "not_run_session_unavailable",
    "deterministic_smoke", "live_passed", "live_failed",
}


def validate(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("schema_version") != "1.0":
        errors.append(
            f"schema_version must be '1.0' (got {data.get('schema_version')!r})"
        )

    industry = data.get("industry")
    if industry not in ALLOWED_INDUSTRIES:
        errors.append(
            f"industry must be one of {sorted(ALLOWED_INDUSTRIES)} "
            f"(got {industry!r})"
        )

    if industry == "other" and not data.get("industry_freetext"):
        errors.append("industry_freetext is required when industry is 'other'")

    areas = data.get("area_of_law", [])
    if not isinstance(areas, list) or not areas:
        errors.append("area_of_law must be a non-empty list")
    else:
        for area in areas:
            if area not in ALLOWED_AREAS:
                errors.append(f"area_of_law contains invalid value {area!r}")

    jurisdictions = data.get("jurisdictions", {})
    primary = jurisdictions.get("primary", [])
    if not isinstance(primary, list) or not primary:
        errors.append("jurisdictions.primary must be a non-empty list")

    secondary = jurisdictions.get("secondary", [])
    if not isinstance(secondary, list):
        errors.append("jurisdictions.secondary must be a list (may be empty)")

    prefs = data.get("output_preferences", {})
    if prefs.get("default_research_mode") not in ALLOWED_RESEARCH_MODES:
        errors.append(
            f"output_preferences.default_research_mode must be one of "
            f"{sorted(ALLOWED_RESEARCH_MODES)} "
            f"(got {prefs.get('default_research_mode')!r})"
        )
    if prefs.get("default_output_mode") not in ALLOWED_OUTPUT_MODES:
        errors.append(
            f"output_preferences.default_output_mode must be one of "
            f"{sorted(ALLOWED_OUTPUT_MODES)} "
            f"(got {prefs.get('default_output_mode')!r})"
        )
    if prefs.get("default_packaging") not in ALLOWED_PACKAGING:
        errors.append(
            f"output_preferences.default_packaging must be one of "
            f"{sorted(ALLOWED_PACKAGING)} "
            f"(got {prefs.get('default_packaging')!r})"
        )
    if prefs.get("default_language") not in ALLOWED_LANGUAGES:
        errors.append(
            f"output_preferences.default_language must be one of "
            f"{sorted(ALLOWED_LANGUAGES)} "
            f"(got {prefs.get('default_language')!r})"
        )

    handoff_owners = data.get("specialist_handoff_owners", [])
    if not isinstance(handoff_owners, list):
        errors.append("specialist_handoff_owners must be a list")

    generated = data.get("generated_knowledge_directories", [])
    if not isinstance(generated, list):
        errors.append("generated_knowledge_directories must be a list")
    else:
        for i, entry in enumerate(generated):
            prefix = f"generated_knowledge_directories[{i}]"
            if not isinstance(entry, dict):
                errors.append(f"{prefix} must be an object")
                continue
            if not isinstance(entry.get("path"), str) or not entry["path"]:
                errors.append(f"{prefix}.path must be a non-empty string")
            if entry.get("review_status") not in ALLOWED_REVIEW_STATUSES:
                errors.append(
                    f"{prefix}.review_status must be one of "
                    f"{sorted(ALLOWED_REVIEW_STATUSES)} "
                    f"(got {entry.get('review_status')!r})"
                )
            if entry.get("source_audit_status") not in ALLOWED_AUDIT_STATUSES:
                errors.append(
                    f"{prefix}.source_audit_status must be one of "
                    f"{sorted(ALLOWED_AUDIT_STATUSES)} "
                    f"(got {entry.get('source_audit_status')!r})"
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Path to a specific config file (default: <root>/user-config.json).",
    )
    args = parser.parse_args(argv)

    config_path = args.config or (args.root / "user-config.json")
    if not config_path.exists():
        print(f"SKIP: {config_path} not present (fresh clone or pre-onboard)")
        return 0

    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: {config_path}: invalid JSON ({exc})", file=sys.stderr)
        return 1

    errors = validate(data)
    if errors:
        for line in errors:
            print(f"FAIL: {config_path}: {line}", file=sys.stderr)
        return 1

    print(f"OK: {config_path} valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
