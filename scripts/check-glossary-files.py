#!/usr/bin/env python3
"""Validate glossary JSON files against references/glossary-schema.md rules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_STATUSES = {"verified", "provisional", "deprecated"}


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_string_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(non_empty_string(item) for item in value)


def iter_glossary_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(path.rglob("glossary-*.json"))


def validate_context_rule(rule: Any, term_ref: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(rule, dict):
        return [f"{term_ref}.context_rules[]: expected object"]
    for key in ("when", "translation"):
        if not non_empty_string(rule.get(key)):
            errors.append(f"{term_ref}.context_rules[].{key}: expected non-empty string")
    for key in ("authority_ids", "pinpoints"):
        if not non_empty_string_list(rule.get(key)):
            errors.append(f"{term_ref}.context_rules[].{key}: expected non-empty string list")
    note = rule.get("note")
    if note is not None and not non_empty_string(note):
        errors.append(f"{term_ref}.context_rules[].note: expected non-empty string when present")
    return errors


def validate_glossary_file(path: Path, root: Path = ROOT) -> list[str]:
    display = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{display}: invalid JSON: {exc}"]

    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{display}: expected object"]

    if data.get("schema_version") != "1.0":
        errors.append(f"{display}.schema_version: must be '1.0'")
    for key in ("jurisdiction", "language_pair", "last_updated"):
        if not non_empty_string(data.get(key)):
            errors.append(f"{display}.{key}: expected non-empty string")

    terms = data.get("terms")
    if not isinstance(terms, list):
        return errors + [f"{display}.terms: expected list"]

    seen_terms: set[str] = set()
    for index, term in enumerate(terms):
        term_ref = f"{display}.terms[{index}]"
        if not isinstance(term, dict):
            errors.append(f"{term_ref}: expected object")
            continue

        term_value = term.get("term")
        if not non_empty_string(term_value):
            errors.append(f"{term_ref}.term: expected non-empty string")
        elif term_value in seen_terms:
            errors.append(f"{term_ref}.term: duplicate term {term_value!r}")
        elif isinstance(term.get("context_rules"), list) and term["context_rules"]:
            seen_terms.add(term_value)
        else:
            seen_terms.add(term_value)

        for key in ("source_language", "preferred_translation", "definition"):
            if not non_empty_string(term.get(key)):
                errors.append(f"{term_ref}.{key}: expected non-empty string")
        for key in ("authority_ids", "pinpoints"):
            if not non_empty_string_list(term.get(key)):
                errors.append(f"{term_ref}.{key}: expected non-empty string list")

        status = term.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{term_ref}.status: unsupported value {status!r}")

        notes = term.get("notes")
        if notes is not None and not non_empty_string(notes):
            errors.append(f"{term_ref}.notes: expected non-empty string when present")

        context_rules = term.get("context_rules")
        if not isinstance(context_rules, list):
            errors.append(f"{term_ref}.context_rules: expected list")
            continue
        for rule in context_rules:
            errors.extend(validate_context_rule(rule, term_ref))

    return errors


def check(path: Path, root: Path = ROOT) -> list[str]:
    target = path if path.is_absolute() else root / path
    if not target.exists():
        return [f"{path}: missing file or directory"]
    errors: list[str] = []
    files = iter_glossary_files(target)
    if not files:
        return [f"{path}: no glossary-*.json files found"]
    for file_path in files:
        errors.extend(validate_glossary_file(file_path, root=root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="tests/fixtures/glossary/valid")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    errors = check(Path(args.path), root=args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: glossary files valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
