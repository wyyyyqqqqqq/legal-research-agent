#!/usr/bin/env python3
"""Check that core quality and source-planning files keep required coverage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MARKERS: dict[str, list[str]] = {
    "CLAUDE.md": [
        "jurisdiction-source-playbook.md",
        "Quality Supremacy",
        "Privacy Handoff",
    ],
    "skills/general-research.md": [
        "Jurisdiction Discipline",
        "supplementary provisions",
        "coverage_gaps",
    ],
    "skills/game-regulation-research.md": [
        "comparison_matrix",
        "co_running_agents",
        "jurisdiction-source-playbook.md",
    ],
    "skills/jurisdiction-source-playbook.md": [
        "Jurisdiction Profile",
        "Source Minimums",
        "Stop Conditions",
    ],
    "skills/result-memo-composition.md": [
        "Required Sections",
        "Route Context",
        "Issue Blocks",
        "Every metadata source",
        "Coverage Gaps",
    ],
    "skills/source-collection.md": [
        "Source Minimum Enforcement",
        "temporal_status",
        "Similar-Statute Guard",
    ],
    "knowledge/general/source-map.md": [
        "United States",
        "European Union",
        "Japan",
        "Minimum Coverage By Deliverable",
    ],
    "knowledge/game-regulation/source-map.md": [
        "Korea",
        "Japan",
        "EU",
        "United States",
    ],
}


def check_markers(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            errors.append(f"{relative_path}: missing file")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative_path}: missing marker {marker!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    errors = check_markers(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: knowledge coverage markers present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
