#!/usr/bin/env python3
"""Validate reference artifact catalog checks."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check-reference-catalog.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_reference_catalog", CHECK_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-reference-catalog.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_valid_reference(root: Path) -> None:
    (root / "references").mkdir(parents=True, exist_ok=True)
    (root / "references/example.md").write_text(
        "# Example Reference\n\n## Required\n\nBody.\n",
        encoding="utf-8",
    )


def write_valid_catalog(root: Path) -> None:
    write_json(
        root / "references/reference-catalog.json",
        {
            "version": "1.0",
            "artifacts": [
                {
                    "id": "example",
                    "kind": "reference",
                    "path": "references/example.md",
                    "status": "active",
                    "min_bytes": 10,
                    "required_headings": ["# Example Reference", "## Required"],
                }
            ],
        },
    )


class ReferenceCatalogTest(unittest.TestCase):
    def test_repository_catalog_is_valid(self) -> None:
        errors = CHECKER.check(REPO_ROOT)
        self.assertEqual(errors, [])

    def test_kind_filter_validates_subset(self) -> None:
        self.assertEqual(CHECKER.check(REPO_ROOT, kind="reference"), [])
        self.assertEqual(CHECKER.check(REPO_ROOT, kind="pack"), [])

    def test_complete_temp_catalog_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_valid_reference(root)
            write_valid_catalog(root)
            self.assertEqual(CHECKER.check(root), [])

    def test_uncataloged_reference_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_valid_reference(root)
            write_json(root / "references/reference-catalog.json", {"version": "1.0", "artifacts": []})
            errors = CHECKER.check(root)
            self.assertTrue(any("not cataloged" in error for error in errors), errors)

    def test_duplicate_id_and_bad_status_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_valid_reference(root)
            write_json(
                root / "references/reference-catalog.json",
                {
                    "version": "1.0",
                    "artifacts": [
                        {
                            "id": "example",
                            "kind": "reference",
                            "path": "references/example.md",
                            "status": "strange",
                            "min_bytes": 10,
                            "required_headings": ["# Example Reference"],
                        },
                        {
                            "id": "example",
                            "kind": "reference",
                            "path": "references/example.md",
                            "status": "active",
                            "min_bytes": 10,
                            "required_headings": ["# Example Reference"],
                        },
                    ],
                },
            )
            errors = CHECKER.check(root)
            self.assertTrue(any("unsupported value 'strange'" in error for error in errors), errors)
            self.assertTrue(any("duplicate artifact id" in error for error in errors), errors)

    def test_missing_heading_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_valid_reference(root)
            write_json(
                root / "references/reference-catalog.json",
                {
                    "version": "1.0",
                    "artifacts": [
                        {
                            "id": "example",
                            "kind": "reference",
                            "path": "references/example.md",
                            "status": "active",
                            "min_bytes": 10,
                            "required_headings": ["## Missing"],
                        }
                    ],
                },
            )
            errors = CHECKER.check(root)
            self.assertTrue(any("missing heading" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
