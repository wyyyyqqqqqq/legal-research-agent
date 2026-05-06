#!/usr/bin/env python3
"""Validate general-law source playbook registry and Markdown files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path("knowledge/general/source-playbook-index.json")
PLAYBOOK_DIR = Path("knowledge/general/playbooks")
REGISTRY_VERSION = "1.0"

ALLOWED_JURISDICTIONS = {"KR", "US", "EU", "JP", "UK", "MULTI"}
ALLOWED_DOMAINS = {
    "administrative",
    "civil_liability",
    "consumer_ecommerce",
    "contracts_commercial",
    "corporate",
    "employment",
    "general",
    "platform_service",
    "tax",
}
ALLOWED_STATUSES = {"draft", "active", "deprecated"}
REQUIRED_METADATA = ("id", "jurisdiction", "domain", "status", "owner", "last_reviewed")
REQUIRED_HEADINGS = (
    "## Metadata",
    "## Scope",
    "## Required Source Layers",
    "## Official Source Entry Points",
    "## Delegated Rule Checks",
    "## Case Law Or Agency Decision Checks",
    "## Currentness Checks",
    "## Common Pitfalls",
    "## Fallback Behavior",
    "## Example Source Plan",
)
NON_EMPTY_HEADINGS = (
    "## Required Source Layers",
    "## Currentness Checks",
    "## Fallback Behavior",
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\{(?:TODO:[^}]+|Title|id|jurisdiction|domain|status|owner|last_reviewed)\}"),
    re.compile(r"\bTODO\b"),
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def relative_display(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def heading_positions(text: str) -> dict[str, int]:
    positions: dict[str, int] = {}
    for heading in REQUIRED_HEADINGS:
        match = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
        if match:
            positions[heading] = match.start()
    return positions


def section_text(text: str, heading: str) -> str:
    match = re.search(rf"(?ms)^{re.escape(heading)}\s*(.*?)(?=^## |\Z)", text)
    return match.group(1).strip() if match else ""


def parse_metadata(text: str) -> dict[str, str]:
    metadata: dict[str, str] = {}
    block = section_text(text, "## Metadata")
    for line in block.splitlines():
        match = re.match(r"^-\s*([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip()
    return metadata


def has_unresolved_placeholder(text: str) -> bool:
    return any(pattern.search(text) for pattern in PLACEHOLDER_PATTERNS)


def validate_registry_entry(entry: Any, index: int) -> tuple[dict[str, str] | None, list[str]]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return None, [f"registry.playbooks[{index}]: expected object"]

    normalized: dict[str, str] = {}
    for key in ("id", "jurisdiction", "domain", "path", "status"):
        value = entry.get(key)
        if not non_empty_string(value):
            errors.append(f"registry.playbooks[{index}].{key}: expected non-empty string")
        else:
            normalized[key] = value.strip()

    jurisdiction = normalized.get("jurisdiction")
    domain = normalized.get("domain")
    status = normalized.get("status")
    path = normalized.get("path")
    if jurisdiction and jurisdiction not in ALLOWED_JURISDICTIONS:
        errors.append(
            f"registry.playbooks[{index}].jurisdiction: unsupported value {jurisdiction!r}"
        )
    if domain and domain not in ALLOWED_DOMAINS:
        errors.append(f"registry.playbooks[{index}].domain: unsupported value {domain!r}")
    if status and status not in ALLOWED_STATUSES:
        errors.append(f"registry.playbooks[{index}].status: unsupported value {status!r}")
    if path and Path(path).is_absolute():
        errors.append(f"registry.playbooks[{index}].path: must be repository-relative")

    return normalized if len(normalized) == 5 else None, errors


def validate_playbook_file(path: Path, entry: dict[str, str], root: Path) -> list[str]:
    errors: list[str] = []
    display = relative_display(path, root)
    text = path.read_text(encoding="utf-8")

    if not re.search(r"(?m)^#\s+\S", text):
        errors.append(f"{display}: missing top-level title")

    positions = heading_positions(text)
    missing = [heading for heading in REQUIRED_HEADINGS if heading not in positions]
    for heading in missing:
        errors.append(f"{display}: missing heading {heading!r}")

    ordered_positions = [positions[heading] for heading in REQUIRED_HEADINGS if heading in positions]
    if ordered_positions != sorted(ordered_positions):
        errors.append(f"{display}: required headings must appear in template order")

    metadata = parse_metadata(text)
    for key in REQUIRED_METADATA:
        if not non_empty_string(metadata.get(key)):
            errors.append(f"{display}: metadata {key!r} is missing or empty")

    for key in ("id", "jurisdiction", "domain", "status"):
        actual = metadata.get(key)
        expected = entry[key]
        if actual and actual != expected:
            errors.append(f"{display}: metadata {key!r}={actual!r} does not match registry {expected!r}")

    for heading in NON_EMPTY_HEADINGS:
        body = section_text(text, heading)
        if not body:
            errors.append(f"{display}: section {heading!r} must be non-empty")

    if has_unresolved_placeholder(text):
        errors.append(f"{display}: unresolved template placeholder remains")

    return errors


def check_source_playbooks(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    registry_path = root / REGISTRY_PATH
    playbook_dir = root / PLAYBOOK_DIR

    if not registry_path.exists():
        return [f"{REGISTRY_PATH}: missing file"]
    if not playbook_dir.exists():
        errors.append(f"{PLAYBOOK_DIR}: missing directory")

    try:
        registry = load_json(registry_path)
    except Exception as exc:
        return [f"{REGISTRY_PATH}: invalid JSON: {exc}"]

    if not isinstance(registry, dict):
        return [f"{REGISTRY_PATH}: expected object"]
    if registry.get("version") != REGISTRY_VERSION:
        errors.append(f"{REGISTRY_PATH}: version must be {REGISTRY_VERSION!r}")

    playbooks = registry.get("playbooks")
    if not isinstance(playbooks, list):
        return errors + [f"{REGISTRY_PATH}: playbooks must be a list"]

    seen_ids: set[str] = set()
    registered_paths: set[Path] = set()
    for index, raw_entry in enumerate(playbooks):
        entry, entry_errors = validate_registry_entry(raw_entry, index)
        errors.extend(entry_errors)
        if entry is None:
            continue

        playbook_id = entry["id"]
        if playbook_id in seen_ids:
            errors.append(f"{REGISTRY_PATH}: duplicate playbook id {playbook_id!r}")
        seen_ids.add(playbook_id)

        relative_path = Path(entry["path"])
        registered_paths.add(relative_path)
        path = root / relative_path
        if not path.exists():
            errors.append(f"{entry['path']}: missing registered playbook file")
            continue
        errors.extend(validate_playbook_file(path, entry, root))

    if playbook_dir.exists():
        for path in sorted(playbook_dir.glob("*.md")):
            relative_path = path.relative_to(root)
            if relative_path not in registered_paths:
                errors.append(f"{relative_path}: playbook file is not registered")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    args = parser.parse_args(argv)

    errors = check_source_playbooks(args.root)
    result = {
        "status": "fail" if errors else "pass",
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        if errors:
            for error in errors:
                print(f"FAIL: {error}", file=sys.stderr)
        else:
            print("OK: source playbooks valid")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
