#!/usr/bin/env python3
"""Unit tests for citation-auditor vendor integration checks."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts" / "check-citation-auditor-vendor.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_citation_auditor_vendor", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-citation-auditor-vendor.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


class CitationAuditorVendorTest(unittest.TestCase):
    def test_repository_vendor_integration_is_valid(self) -> None:
        self.assertEqual(CHECKER.check_vendor(ROOT, run_cli=False), [])

    def test_missing_vendor_path_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            errors = CHECKER.check_vendor(root, run_cli=False)
            self.assertTrue(any("missing vendored citation-auditor path" in error for error in errors), errors)

    def test_vendor_version_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for relative_path in CHECKER.REQUIRED_PATHS:
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                if relative_path.endswith("VENDOR.md"):
                    path.write_text("- Version: **v0.0.0**\n", encoding="utf-8")
                else:
                    path.write_text("placeholder\n", encoding="utf-8")

            errors = CHECKER.check_vendor(root, expected_version="1.4.0", run_cli=False)
            self.assertTrue(any("vendor version mismatch" in error for error in errors), errors)

    def test_symlinked_vendor_path_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / "target-skill.md"
            target.write_text("placeholder\n", encoding="utf-8")
            for relative_path in CHECKER.REQUIRED_PATHS:
                path = root / relative_path
                path.parent.mkdir(parents=True, exist_ok=True)
                if relative_path == ".claude/skills/citation-auditor/SKILL.md":
                    path.symlink_to(target)
                elif relative_path.endswith("VENDOR.md"):
                    path.write_text("- Version: **v1.4.0**\n", encoding="utf-8")
                else:
                    path.write_text("placeholder\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[project]\ndependencies = ['marko>=2.1.0', 'pydantic>=2.7.0']\n",
                encoding="utf-8",
            )

            errors = CHECKER.check_vendor(root, run_cli=False)
            self.assertTrue(any("must not be a symlink" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
