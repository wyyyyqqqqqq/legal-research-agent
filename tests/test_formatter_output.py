#!/usr/bin/env python3
"""Unit tests for standalone formatter output validation."""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts" / "check-formatter-output.py"
KO_FIXTURE = ROOT / "tests" / "fixtures" / "formatter" / "ko-standalone"
EN_FIXTURE = ROOT / "tests" / "fixtures" / "formatter" / "en-standalone"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_formatter_output", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-formatter-output.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


class FormatterOutputTest(unittest.TestCase):
    def test_fixture_root_passes(self) -> None:
        self.assertEqual(CHECKER.validate_fixture_root(ROOT / "tests" / "fixtures" / "formatter"), [])

    def test_valid_korean_fixture_passes(self) -> None:
        errors = CHECKER.validate_formatter_output(
            KO_FIXTURE / "formatted.md",
            KO_FIXTURE / "legal-research-agent-meta.json",
            language="ko",
        )
        self.assertEqual(errors, [])

    def test_valid_english_fixture_passes(self) -> None:
        errors = CHECKER.validate_formatter_output(
            EN_FIXTURE / "formatted.md",
            EN_FIXTURE / "legal-research-agent-meta.json",
            language="en",
        )
        self.assertEqual(errors, [])

    def test_missing_required_section_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copytree(KO_FIXTURE, temp_path / "case")
            formatted = temp_path / "case" / "formatted.md"
            text = formatted.read_text(encoding="utf-8").replace("## 검토의견\n\n", "")
            formatted.write_text(text, encoding="utf-8")
            errors = CHECKER.validate_formatter_output(
                formatted,
                temp_path / "case" / "legal-research-agent-meta.json",
                language="ko",
            )
        self.assertTrue(any("검토의견" in error for error in errors), errors)

    def test_unknown_source_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copytree(EN_FIXTURE, temp_path / "case")
            formatted = temp_path / "case" / "formatted.md"
            text = formatted.read_text(encoding="utf-8").replace("src_001", "src_999", 1)
            formatted.write_text(text, encoding="utf-8")
            errors = CHECKER.validate_formatter_output(
                formatted,
                temp_path / "case" / "legal-research-agent-meta.json",
                language="en",
            )
        self.assertTrue(any("unknown source ids" in error for error in errors), errors)

    def test_missing_source_table_row_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copytree(KO_FIXTURE, temp_path / "case")
            formatted = temp_path / "case" / "formatted.md"
            text = formatted.read_text(encoding="utf-8").replace(
                "| src_001 | A | Official game-regulation source placeholder | Placeholder article | Placeholder pinpoint | official source placeholder |\n",
                "",
            )
            formatted.write_text(text, encoding="utf-8")
            errors = CHECKER.validate_formatter_output(
                formatted,
                temp_path / "case" / "legal-research-agent-meta.json",
                language="ko",
            )
        self.assertTrue(any("missing source table rows" in error for error in errors), errors)

    def test_unanchored_material_paragraph_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copytree(EN_FIXTURE, temp_path / "case")
            formatted = temp_path / "case" / "formatted.md"
            text = formatted.read_text(encoding="utf-8").replace(
                "That framing is anchored\n"
                "to src_001 and should not be converted into a definitive sanction conclusion\n"
                "without current official-source verification.",
                "That framing should not be converted into a definitive sanction conclusion\n"
                "without current official-source verification.",
            )
            formatted.write_text(text, encoding="utf-8")
            errors = CHECKER.validate_formatter_output(
                formatted,
                temp_path / "case" / "legal-research-agent-meta.json",
                language="en",
            )
        self.assertTrue(any("source_anchoring" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
