#!/usr/bin/env python3
"""Validate glossary JSON fixture checks."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check-glossary-files.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_glossary_files", CHECK_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-glossary-files.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


class GlossaryFilesTest(unittest.TestCase):
    def test_valid_fixture_passes(self) -> None:
        errors = CHECKER.check(Path("tests/fixtures/glossary/valid"), root=REPO_ROOT)
        self.assertEqual(errors, [])

    def test_missing_source_fixture_fails(self) -> None:
        errors = CHECKER.check(
            Path("tests/fixtures/glossary/invalid-missing-source"),
            root=REPO_ROOT,
        )
        self.assertTrue(any("authority_ids" in error for error in errors), errors)

    def test_bad_status_fixture_fails(self) -> None:
        errors = CHECKER.check(
            Path("tests/fixtures/glossary/invalid-bad-status"),
            root=REPO_ROOT,
        )
        self.assertTrue(any("unsupported value 'maybe'" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
