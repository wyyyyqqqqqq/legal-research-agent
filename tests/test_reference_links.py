#!/usr/bin/env python3
"""Validate internal reference-link checker."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check-reference-links.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_reference_links", CHECK_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-reference-links.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


class ReferenceLinksTest(unittest.TestCase):
    def test_repository_links_resolve(self) -> None:
        errors = CHECKER.check(REPO_ROOT)
        self.assertEqual(errors, [])

    def test_missing_reference_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "skills").mkdir()
            (root / "skills" / "example.md").write_text(
                "Use `references/missing.md` for details.\n",
                encoding="utf-8",
            )
            errors = CHECKER.check(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("references/missing.md", errors[0])

    def test_markdown_link_target_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "references").mkdir()
            (root / "references" / "exists.md").write_text("# Exists\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[ok](references/exists.md)\n[bad](references/missing.md)\n",
                encoding="utf-8",
            )
            errors = CHECKER.check(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("references/missing.md", errors[0])

    def test_angle_wrapped_markdown_link_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "README.md").write_text(
                "[bad](<references/missing.md>)\n",
                encoding="utf-8",
            )
            errors = CHECKER.check(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("references/missing.md", errors[0])

    def test_relative_markdown_link_to_reference_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            docs = root / "docs"
            docs.mkdir()
            (docs / "guide.md").write_text(
                "[bad](../references/missing.md)\n",
                encoding="utf-8",
            )
            errors = CHECKER.check(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("references/missing.md", errors[0])

    def test_archive_is_skipped_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive = root / "docs" / "archive" / "plans"
            archive.mkdir(parents=True)
            (archive / "old.md").write_text(
                "Historical pointer: `references/missing.md`.\n",
                encoding="utf-8",
            )
            self.assertEqual(CHECKER.check(root), [])
            self.assertEqual(len(CHECKER.check(root, include_archive=True)), 1)


if __name__ == "__main__":
    unittest.main()
