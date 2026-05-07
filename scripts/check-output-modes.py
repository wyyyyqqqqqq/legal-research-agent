#!/usr/bin/env python3
"""Validate output-mode templates and frameworks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_TEMPLATE_SECTIONS: dict[str, list[str]] = {
    "templates/output-modes/executive-brief.md": [
        "## Scope and As-of Date",
        "## Key Conclusions",
        "## Counter-Analysis and Risk Assessment",
        "## Risk and Priority Ranking",
        "## Practical Implications",
        "## Immediate Action Checklist",
        "## Top Sources",
        "## Verification Guide",
    ],
    "templates/output-modes/comparative-matrix.md": [
        "## Scope and As-of Date",
        "## Comparative Matrix",
        "## Divergence Commentary",
        "## Counter-Analysis",
        "## Practical Implications",
        "## Annotated Bibliography",
        "## Verification Guide",
    ],
    "templates/output-modes/enforcement-case-law.md": [
        "## Scope and As-of Date",
        "## Conclusion Summary",
        "## Enforcement Timeline",
        "## Case and Decision Summaries",
        "## Counter-Analysis",
        "## Practical Implications",
        "## Annotated Bibliography",
        "## Verification Guide",
    ],
    "templates/output-modes/black-letter-commentary.md": [
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

REQUIRED_FRAMEWORK_MARKERS: dict[str, list[str]] = {
    "knowledge/output-modes/comparative-framework.md": [
        "## Standard Axes",
        "Regulatory Scope",
        "Obligated Parties",
        "Key Obligations",
        "Exemptions and Safe Harbors",
        "Sanctions and Penalties",
        "Competent Authority",
        "Effective Date and Transition",
        "Extraterritorial Reach",
        "Cross-Border Mechanisms",
        "Pending Reforms",
        "## Divergence Commentary Rules",
        "## Practical Implications (Mandatory)",
    ],
    "knowledge/output-modes/counter-analysis-checklist.md": [
        "Alternative Interpretation",
        "Minority or Dissenting View",
        "Jurisdictional Risk",
        "Factual Sensitivity",
        "Practical Enforcement Risk",
        "Similar-Statute Confusion",
        "## Per-Mode Minimums",
        "executive_brief",
        "comparative_matrix",
        "enforcement_case_law",
        "black_letter_commentary",
        "canonical",
    ],
    "knowledge/output-modes/mode-index.md": [
        "executive_brief",
        "comparative_matrix",
        "enforcement_case_law",
        "black_letter_commentary",
        "canonical",
        "counter-analysis",
        "comparative-framework",
    ],
}


def check(root: Path) -> list[str]:
    errors: list[str] = []
    for relative, sections in REQUIRED_TEMPLATE_SECTIONS.items():
        path = root / relative
        if not path.exists():
            errors.append(f"{relative}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        for section in sections:
            if section not in text:
                errors.append(f"{relative}: missing required section {section!r}")
    for relative, markers in REQUIRED_FRAMEWORK_MARKERS.items():
        path = root / relative
        if not path.exists():
            errors.append(f"{relative}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative}: missing required marker {marker!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    errors = check(args.root)
    if errors:
        for line in errors:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print("OK: output-mode templates and frameworks valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
