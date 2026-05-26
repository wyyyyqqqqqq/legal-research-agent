#!/usr/bin/env python3
"""Validate references/packs/ through the shared reference catalog."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_CHECKER = ROOT / "scripts" / "check-reference-catalog.py"


def load_catalog_checker():
    spec = importlib.util.spec_from_file_location("check_reference_catalog", CATALOG_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {CATALOG_CHECKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(root: Path) -> list[str]:
    checker = load_catalog_checker()
    return checker.check(root, kind="pack")


def pack_count(root: Path) -> int:
    checker = load_catalog_checker()
    errors, summary = checker.validate_catalog(root, kind="pack")
    if errors:
        return 0
    return int(summary["by_kind"].get("pack", 0))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    errors = check(args.root)
    if errors:
        for line in errors:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print(f"OK: {pack_count(args.root)} reference packs present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
