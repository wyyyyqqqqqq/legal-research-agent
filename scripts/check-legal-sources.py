#!/usr/bin/env python3
"""Validate legal_sources.yaml schema."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "legal_sources.yaml"
CLI_PATH = ROOT / "scripts" / "legal_source_registry.py"


def _load_cli():
    spec = importlib.util.spec_from_file_location("legal_source_registry", CLI_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load legal_source_registry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    args = parser.parse_args(argv)

    if not args.registry.exists():
        print(f"FAIL: registry not found at {args.registry}", file=sys.stderr)
        return 1

    cli = _load_cli()
    text = args.registry.read_text(encoding="utf-8")
    data = cli.parse_registry(text)
    errors = cli.cmd_validate(data)
    if errors:
        for line in errors:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print(f"OK: {args.registry} valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
