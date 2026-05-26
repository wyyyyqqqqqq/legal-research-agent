#!/usr/bin/env python3
"""Validate the reference artifact catalog and cataloged files."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = Path("references/reference-catalog.json")
CATALOG_VERSION = "1.0"
ALLOWED_KINDS = {"reference", "pack"}
ALLOWED_STATUSES = {"draft", "active", "deprecated"}
INLINE_IGNORE_MARKERS = {
    "legacy path",
    "historical reference",
    "archive-only",
    "intentionally missing",
    "unresolved example",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def relative_display(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def discover_reference_files(root: Path) -> set[str]:
    refs_dir = root / "references"
    packs_dir = refs_dir / "packs"
    discovered: set[str] = set()
    if refs_dir.exists():
        for path in refs_dir.glob("*.md"):
            discovered.add(str(path.relative_to(root)))
    if packs_dir.exists():
        for path in packs_dir.glob("*.md"):
            discovered.add(str(path.relative_to(root)))
    return discovered


def expected_kind_for_path(path: str) -> str | None:
    relative = Path(path)
    if relative.parts[:2] == ("references", "packs") and relative.suffix == ".md":
        return "pack"
    if len(relative.parts) == 2 and relative.parts[0] == "references" and relative.suffix == ".md":
        return "reference"
    return None


def skill_exists(root: Path, skill: str) -> bool:
    return (root / "skills" / f"{skill}.md").exists() or (
        root / "skills" / "specialists" / f"{skill}.md"
    ).exists()


def line_is_ignored(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in INLINE_IGNORE_MARKERS)


def active_skill_references(root: Path, target: str) -> list[str]:
    hits: list[str] = []
    skills_dir = root / "skills"
    if not skills_dir.exists():
        return hits
    for path in sorted(skills_dir.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line_is_ignored(line):
                continue
            if target in line:
                hits.append(f"{relative_display(path, root)}:{lineno}")
    return hits


def validate_entry(
    root: Path,
    entry: Any,
    index: int,
    *,
    kind_filter: str | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return None, [f"artifacts[{index}]: expected object"]

    normalized: dict[str, Any] = {}
    for key in ("id", "kind", "path", "status"):
        value = entry.get(key)
        if not non_empty_string(value):
            errors.append(f"artifacts[{index}].{key}: expected non-empty string")
        else:
            normalized[key] = value.strip()

    artifact_id = normalized.get("id")
    kind = normalized.get("kind")
    path_value = normalized.get("path")
    status = normalized.get("status")

    if kind and kind not in ALLOWED_KINDS:
        errors.append(f"artifacts[{index}].kind: unsupported value {kind!r}")
    if status and status not in ALLOWED_STATUSES:
        errors.append(f"artifacts[{index}].status: unsupported value {status!r}")
    if path_value and Path(path_value).is_absolute():
        errors.append(f"artifacts[{index}].path: must be repository-relative")
    expected_kind = expected_kind_for_path(path_value or "")
    if path_value and expected_kind is None:
        errors.append(
            f"artifacts[{index}].path: must be references/*.md or references/packs/*.md"
        )
    if kind and expected_kind and kind != expected_kind:
        errors.append(
            f"artifacts[{index}].kind: {kind!r} does not match path kind {expected_kind!r}"
        )
    if artifact_id and path_value and artifact_id != Path(path_value).stem:
        errors.append(
            f"artifacts[{index}].id: {artifact_id!r} must match path stem {Path(path_value).stem!r}"
        )
    if kind_filter and kind and kind != kind_filter:
        return normalized if not errors else None, errors

    min_bytes = entry.get("min_bytes")
    if not isinstance(min_bytes, int) or min_bytes <= 0:
        errors.append(f"artifacts[{index}].min_bytes: expected positive integer")
    else:
        normalized["min_bytes"] = min_bytes

    headings = entry.get("required_headings")
    if not isinstance(headings, list) or not headings:
        errors.append(f"artifacts[{index}].required_headings: expected non-empty list")
    else:
        normalized_headings: list[str] = []
        for heading_index, heading in enumerate(headings):
            if not non_empty_string(heading):
                errors.append(
                    f"artifacts[{index}].required_headings[{heading_index}]: expected non-empty string"
                )
            else:
                normalized_headings.append(heading.strip())
        normalized["required_headings"] = normalized_headings

    owner_skill = entry.get("owner_skill")
    if owner_skill is not None:
        if not non_empty_string(owner_skill):
            errors.append(f"artifacts[{index}].owner_skill: expected non-empty string")
        elif not skill_exists(root, owner_skill.strip()):
            errors.append(
                f"artifacts[{index}].owner_skill: skill {owner_skill.strip()!r} not found"
            )
        else:
            normalized["owner_skill"] = owner_skill.strip()

    owner_doc = entry.get("owner_doc")
    if owner_doc is not None:
        if not non_empty_string(owner_doc):
            errors.append(f"artifacts[{index}].owner_doc: expected non-empty string")
        elif not (root / owner_doc.strip()).exists():
            errors.append(f"artifacts[{index}].owner_doc: file {owner_doc.strip()!r} not found")
        else:
            normalized["owner_doc"] = owner_doc.strip()

    if path_value:
        artifact_path = root / path_value
        if not artifact_path.exists():
            errors.append(f"{path_value}: missing cataloged file")
        else:
            size = artifact_path.stat().st_size
            if isinstance(min_bytes, int) and size < min_bytes:
                errors.append(
                    f"{path_value}: too small ({size} bytes < {min_bytes}); artifact appears empty"
                )
            text = artifact_path.read_text(encoding="utf-8")
            for heading in normalized.get("required_headings", []):
                if heading not in text:
                    errors.append(f"{path_value}: missing heading {heading!r}")

    if status == "deprecated" and path_value:
        refs = active_skill_references(root, path_value)
        for ref in refs:
            errors.append(f"{path_value}: deprecated artifact referenced by active skill at {ref}")

    return normalized if not errors else None, errors


def validate_catalog(root: Path = ROOT, kind: str | None = None) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    catalog_path = root / CATALOG_PATH
    if not catalog_path.exists():
        return [f"{CATALOG_PATH}: missing file"], {}

    try:
        catalog = load_json(catalog_path)
    except Exception as exc:
        return [f"{CATALOG_PATH}: invalid JSON: {exc}"], {}

    if not isinstance(catalog, dict):
        return [f"{CATALOG_PATH}: expected object"], {}
    if catalog.get("version") != CATALOG_VERSION:
        errors.append(f"{CATALOG_PATH}: version must be {CATALOG_VERSION!r}")

    artifacts = catalog.get("artifacts")
    if not isinstance(artifacts, list):
        return errors + [f"{CATALOG_PATH}: artifacts must be a list"], {}

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()
    normalized_entries: list[dict[str, Any]] = []

    for index, raw_entry in enumerate(artifacts):
        entry, entry_errors = validate_entry(root, raw_entry, index, kind_filter=kind)
        errors.extend(entry_errors)
        if not isinstance(raw_entry, dict):
            continue
        artifact_kind = raw_entry.get("kind")
        if kind and artifact_kind != kind:
            continue

        artifact_id = raw_entry.get("id")
        path_value = raw_entry.get("path")
        if non_empty_string(artifact_id):
            if artifact_id in seen_ids:
                errors.append(f"{CATALOG_PATH}: duplicate artifact id {artifact_id!r}")
            seen_ids.add(artifact_id)
        if non_empty_string(path_value):
            if path_value in seen_paths:
                errors.append(f"{CATALOG_PATH}: duplicate artifact path {path_value!r}")
            seen_paths.add(path_value)
        if entry is not None:
            normalized_entries.append(entry)

    discovered = discover_reference_files(root)
    if kind:
        discovered = {
            path for path in discovered if expected_kind_for_path(path) == kind
        }
    for path in sorted(discovered - seen_paths):
        errors.append(f"{path}: reference artifact file is not cataloged")

    summary = build_report(normalized_entries, errors)
    return errors, summary


def build_report(entries: list[dict[str, Any]], errors: list[str]) -> dict[str, Any]:
    by_kind = Counter(str(entry.get("kind", "")) for entry in entries)
    by_status = Counter(str(entry.get("status", "")) for entry in entries)
    return {
        "status": "fail" if errors else "pass",
        "total": len(entries),
        "by_kind": dict(sorted(by_kind.items())),
        "by_status": dict(sorted(by_status.items())),
        "deprecated_pointed_to_by_active_skills": [
            error for error in errors if "deprecated artifact referenced" in error
        ],
        "uncataloged_files": [
            error for error in errors if "reference artifact file is not cataloged" in error
        ],
        "missing_required_headings": [
            error for error in errors if ": missing heading " in error
        ],
        "errors": errors,
    }


def check(root: Path = ROOT, kind: str | None = None) -> list[str]:
    errors, _summary = validate_catalog(root, kind=kind)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--kind", choices=sorted(ALLOWED_KINDS))
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    parser.add_argument("--report-json", type=Path, help="Write validation report JSON.")
    args = parser.parse_args(argv)

    errors, summary = validate_catalog(args.root, kind=args.kind)
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    elif errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
    else:
        label = f" {args.kind}" if args.kind else ""
        print(f"OK:{label} reference catalog valid ({summary['total']} artifacts)")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
