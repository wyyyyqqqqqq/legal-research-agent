#!/usr/bin/env python3
"""Validate local smoke fixture shape."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE_DIR = ROOT / "tests" / "fixtures" / "cases"
RESEARCH_MODES = {"general", "game_regulation", "game_plus_general", "fallback"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_fixture(path: Path) -> list[str]:
    errors: list[str] = []
    data = load_json(path)
    if not isinstance(data, dict):
        return [f"{path}: fixture must be object"]
    required = {
        "id",
        "title",
        "user_question",
        "expected_research_mode",
        "jurisdictions",
        "domains",
    }
    missing = sorted(required - set(data))
    if missing:
        errors.append(f"{path}: missing keys {missing}")
    if data.get("expected_research_mode") not in RESEARCH_MODES:
        errors.append(f"{path}: invalid expected_research_mode {data.get('expected_research_mode')!r}")
    for key in ("jurisdictions", "domains"):
        if key in data and not isinstance(data[key], list):
            errors.append(f"{path}: {key} must be list")
    if not isinstance(data.get("user_question"), str) or not data.get("user_question", "").strip():
        errors.append(f"{path}: user_question must be non-empty string")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-dir", type=Path, default=DEFAULT_FIXTURE_DIR)
    args = parser.parse_args(argv)

    if not args.fixture_dir.exists():
        print(f"FAIL: fixture directory does not exist: {args.fixture_dir}", file=sys.stderr)
        return 1

    fixture_paths = sorted(args.fixture_dir.glob("*.json"))
    if not fixture_paths:
        print(f"FAIL: no fixture JSON files found in {args.fixture_dir}", file=sys.stderr)
        return 1

    errors: list[str] = []
    ids: set[str] = set()
    for path in fixture_paths:
        errors.extend(validate_fixture(path))
        data = load_json(path)
        fixture_id = data.get("id") if isinstance(data, dict) else None
        if fixture_id in ids:
            errors.append(f"{path}: duplicate fixture id {fixture_id!r}")
        if isinstance(fixture_id, str):
            ids.add(fixture_id)

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(f"OK: {len(fixture_paths)} smoke fixtures valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
