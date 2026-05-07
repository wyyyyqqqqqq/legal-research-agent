#!/usr/bin/env python3
"""Legal sources registry CLI — validate / list / show.

The registry file (legal_sources.yaml at the project root) declares
jurisdiction-source priority, MCP fallback policy, and Grade
defaults. This script avoids the PyYAML dependency by parsing the
limited subset of YAML our schema actually uses.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "legal_sources.yaml"

REQUIRED_TOP_KEYS = {"schema_version", "jurisdictions"}


def parse_registry(text: str) -> dict:
    """Tiny, schema-aware YAML reader. Returns a nested dict.

    Supports only the constructs used in legal_sources.yaml:
      key: value
      key:
        nested-key: value
      - item
    """
    lines = text.splitlines()
    root: dict = {}
    stack: list[tuple[int, dict | list]] = [(0, root)]
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        # Pop stack until indent fits
        while stack and indent < stack[-1][0]:
            stack.pop()
        container = stack[-1][1] if stack else root

        if stripped.startswith("- "):
            # List item
            value = stripped[2:].strip()
            if isinstance(container, list):
                if ":" in value:
                    # Inline mapping inside list
                    new_obj: dict = {}
                    container.append(new_obj)
                    stack.append((indent + 2, new_obj))
                    # Re-process this line as nested fields
                    key, _, val = value.partition(":")
                    new_obj[key.strip()] = _parse_scalar(val.strip())
                else:
                    container.append(_parse_scalar(value))
            i += 1
            continue

        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # Nested object or list follows
                # Peek ahead to determine
                next_indent = indent + 2
                next_kind: dict | list = {}
                if i + 1 < len(lines):
                    for j in range(i + 1, len(lines)):
                        if not lines[j].strip() or lines[j].lstrip().startswith("#"):
                            continue
                        peek = lines[j]
                        peek_indent = len(peek) - len(peek.lstrip(" "))
                        if peek_indent <= indent:
                            break
                        if peek.lstrip().startswith("- "):
                            next_kind = []
                        break
                if isinstance(container, dict):
                    container[key] = next_kind
                    stack.append((next_indent, next_kind))
                i += 1
                continue
            else:
                if isinstance(container, dict):
                    container[key] = _parse_scalar(value)
                i += 1
                continue
        i += 1
    return root


def _parse_scalar(value: str):
    if value in ("null", "~", ""):
        return None
    if value in ("true", "True"):
        return True
    if value in ("false", "False"):
        return False
    if value == "[]":
        return []
    if value == "{}":
        return {}
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    return value


def cmd_validate(data: dict) -> list[str]:
    errors: list[str] = []
    missing_top = REQUIRED_TOP_KEYS - set(data)
    if missing_top:
        errors.append(f"missing top-level keys: {sorted(missing_top)}")
    if data.get("schema_version") != "1.0":
        errors.append(
            f"schema_version must be '1.0' (got {data.get('schema_version')!r})"
        )
    jurisdictions = data.get("jurisdictions") or {}
    if not isinstance(jurisdictions, dict) or not jurisdictions:
        errors.append("jurisdictions must be a non-empty mapping")
    else:
        for code, entry in jurisdictions.items():
            if not isinstance(entry, dict):
                errors.append(f"jurisdictions.{code}: entry must be a mapping")
                continue
            primary = entry.get("primary")
            if not isinstance(primary, list) or not primary:
                errors.append(f"jurisdictions.{code}.primary must be a non-empty list")
            secondary = entry.get("secondary")
            if secondary is not None and not isinstance(secondary, list):
                errors.append(f"jurisdictions.{code}.secondary must be a list (or null)")
    return errors


def cmd_list(data: dict) -> list[str]:
    out = []
    for code, entry in (data.get("jurisdictions") or {}).items():
        primary_count = len(entry.get("primary") or [])
        secondary_count = len(entry.get("secondary") or [])
        out.append(f"{code}: primary={primary_count} secondary={secondary_count}")
    return out


def cmd_show(data: dict, jurisdiction: str) -> list[str]:
    entry = (data.get("jurisdictions") or {}).get(jurisdiction)
    if not entry:
        return [f"jurisdiction {jurisdiction!r} not found"]
    out = [f"== {jurisdiction} =="]
    for source in entry.get("primary") or []:
        out.append(f"  primary: {source.get('name', '?')} -> {source.get('url', '')}")
    for source in entry.get("secondary") or []:
        out.append(f"  secondary: {source.get('name', '?')}")
    if entry.get("mcp_fallback"):
        out.append(f"  mcp: {entry['mcp_fallback'].get('mcp_id', '?')}")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("validate", "list", "show"),
    )
    parser.add_argument("jurisdiction", nargs="?", default=None)
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    args = parser.parse_args(argv)

    if not args.registry.exists():
        print(f"FAIL: registry not found at {args.registry}", file=sys.stderr)
        return 1

    text = args.registry.read_text(encoding="utf-8")
    data = parse_registry(text)

    if args.command == "validate":
        errors = cmd_validate(data)
        if errors:
            for line in errors:
                print(f"FAIL: {line}", file=sys.stderr)
            return 1
        print("OK: registry valid")
        return 0
    if args.command == "list":
        for line in cmd_list(data):
            print(line)
        return 0
    if args.command == "show":
        if not args.jurisdiction:
            print("FAIL: 'show' requires a jurisdiction code", file=sys.stderr)
            return 1
        for line in cmd_show(data, args.jurisdiction):
            print(line)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
