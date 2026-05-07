#!/usr/bin/env python3
"""Validate skills/specialists/ catalog and structure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SPECIALISTS = {
    "antitrust-investigation-summary",
    "api-acceptable-use-policy",
    "cyber-law-compliance-summary",
    "gambling-law-summary",
    "ip-infringement-analysis",
    "privacy-law-updates",
    "regulatory-summary",
    "terms-of-service",
}


def check(root: Path) -> list[str]:
    errors: list[str] = []
    specialist_dir = root / "skills" / "specialists"
    if not specialist_dir.is_dir():
        errors.append("skills/specialists/: directory missing")
        return errors

    actual = {p.stem for p in specialist_dir.glob("*.md")}
    missing = EXPECTED_SPECIALISTS - actual
    extra = actual - EXPECTED_SPECIALISTS

    for name in sorted(missing):
        errors.append(f"skills/specialists/: missing expected skill {name!r}")
    for name in sorted(extra):
        errors.append(
            f"skills/specialists/{name}.md: not in expected catalog "
            f"(update EXPECTED_SPECIALISTS or remove the file)"
        )

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
    print(f"OK: {len(EXPECTED_SPECIALISTS)} specialist skills present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
