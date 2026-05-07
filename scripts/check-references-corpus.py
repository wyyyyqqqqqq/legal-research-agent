#!/usr/bin/env python3
"""Validate references/ public corpus (non-pack files)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_REFERENCES = {
    "comparative-framework",
    "counter-analysis-checklist",
    "korean-law-reference",
    "legal-writing-formatting-guide",
    "source-payload-contract",
}

MIN_BYTES = 1000


def check(root: Path) -> list[str]:
    errors: list[str] = []
    refs_dir = root / "references"
    if not refs_dir.is_dir():
        errors.append("references/: directory missing")
        return errors

    actual = {p.stem for p in refs_dir.glob("*.md")}
    missing = EXPECTED_REFERENCES - actual

    for name in sorted(missing):
        errors.append(f"references/: missing expected reference {name!r}")
    for name in sorted(actual & EXPECTED_REFERENCES):
        path = refs_dir / f"{name}.md"
        size = path.stat().st_size
        if size < MIN_BYTES:
            errors.append(
                f"references/{name}.md: too small ({size} bytes "
                f"< {MIN_BYTES}); reference appears empty or truncated"
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
    print(f"OK: {len(EXPECTED_REFERENCES)} public references present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
