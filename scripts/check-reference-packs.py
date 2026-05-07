#!/usr/bin/env python3
"""Validate references/packs/ catalog and structure."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_PACKS = {
    "antitrust-investigation-summary",
    "api-acceptable-use-policy",
    "cyber-law-compliance-summary",
    "gambling-law-summary",
    "ip-infringement-analysis",
    "terms-of-service",
}

# Confirm a real vendor copy, not an empty placeholder.
MIN_BYTES = 1500


def check(root: Path) -> list[str]:
    errors: list[str] = []
    packs_dir = root / "references" / "packs"
    if not packs_dir.is_dir():
        errors.append("references/packs/: directory missing")
        return errors

    actual = {p.stem for p in packs_dir.glob("*.md")}
    missing = EXPECTED_PACKS - actual
    extra = actual - EXPECTED_PACKS

    for name in sorted(missing):
        errors.append(f"references/packs/: missing expected pack {name!r}")
    for name in sorted(extra):
        errors.append(
            f"references/packs/{name}.md: not in expected catalog "
            f"(update EXPECTED_PACKS or remove the file)"
        )
    for name in sorted(actual & EXPECTED_PACKS):
        path = packs_dir / f"{name}.md"
        size = path.stat().st_size
        if size < MIN_BYTES:
            errors.append(
                f"references/packs/{name}.md: too small ({size} bytes "
                f"< {MIN_BYTES}); pack appears empty or truncated"
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
    print(f"OK: {len(EXPECTED_PACKS)} reference packs present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
