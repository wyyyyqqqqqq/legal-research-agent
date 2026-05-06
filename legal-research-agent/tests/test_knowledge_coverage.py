#!/usr/bin/env python3
"""Unit tests for core legal-research knowledge coverage markers."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COVERAGE_PATH = ROOT / "scripts" / "check-knowledge-coverage.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_knowledge_coverage", COVERAGE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-knowledge-coverage.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


class KnowledgeCoverageTest(unittest.TestCase):
    def test_required_coverage_markers_are_present(self) -> None:
        self.assertEqual(CHECKER.check_markers(ROOT), [])

    def test_formatter_profiles_are_required(self) -> None:
        required_paths = set(CHECKER.REQUIRED_MARKERS)
        self.assertIn("skills/legal-writing-formatter.md", required_paths)
        self.assertIn("docs/standalone-workflow.md", required_paths)
        self.assertIn("knowledge/legal-writing/formatter-index.md", required_paths)
        self.assertIn("knowledge/legal-writing/docx-ready-markdown-profile.md", required_paths)
        self.assertIn("knowledge/legal-writing/ko-formatter-profile.md", required_paths)
        self.assertIn("knowledge/legal-writing/en-formatter-profile.md", required_paths)


if __name__ == "__main__":
    unittest.main()
