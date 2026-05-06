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

    def test_source_playbook_scaffold_is_required(self) -> None:
        required_paths = set(CHECKER.REQUIRED_MARKERS)
        self.assertIn("templates/source-playbook.example.md", required_paths)
        self.assertIn("docs/source-playbook-authoring.md", required_paths)
        self.assertIn("knowledge/general/source-playbook-index.json", required_paths)

    def test_general_law_source_playbook_is_required(self) -> None:
        required_paths = set(CHECKER.REQUIRED_MARKERS)
        self.assertIn("skills/general-law-source-playbook.md", required_paths)
        self.assertIn("knowledge/general/domain-source-checklist.md", required_paths)
        self.assertIn("knowledge/general/playbooks/kr-platform-service.md", required_paths)

    def test_currentness_gate_is_required(self) -> None:
        required_paths = set(CHECKER.REQUIRED_MARKERS)
        self.assertIn("skills/currentness-check.md", required_paths)
        self.assertIn("skills/source-grading.md", required_paths)
        self.assertIn("skills/quality-check.md", required_paths)

    def test_claim_verification_gate_is_required(self) -> None:
        required_paths = set(CHECKER.REQUIRED_MARKERS)
        self.assertIn("skills/claim-verification-loop.md", required_paths)
        self.assertIn("skills/claim-spot-check.md", required_paths)
        self.assertIn("skills/output-contract.md", required_paths)


if __name__ == "__main__":
    unittest.main()
