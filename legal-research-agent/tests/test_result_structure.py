#!/usr/bin/env python3
"""Unit tests for result markdown structure validation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STRUCTURE_PATH = ROOT / "scripts" / "check-result-structure.py"
VALID_OUTPUT = ROOT / "tests" / "fixtures" / "output" / "valid"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_result_structure", STRUCTURE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-result-structure.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


def valid_meta() -> dict:
    return json.loads((VALID_OUTPUT / "legal-research-agent-meta.json").read_text(encoding="utf-8"))


class ResultStructureTest(unittest.TestCase):
    def write_output(self, result_text: str, meta: dict | None = None) -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "legal-research-agent-result.md").write_text(result_text, encoding="utf-8")
        (temp_dir / "legal-research-agent-meta.json").write_text(
            json.dumps(meta or valid_meta(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return temp_dir

    def test_valid_fixture_has_required_structure(self) -> None:
        self.assertEqual(CHECKER.check_result_structure(VALID_OUTPUT), [])

    def test_missing_required_heading_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        output_dir = self.write_output(text.replace("## Coverage Gaps\n", ""))
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("Coverage Gaps" in error for error in errors), errors)

    def test_unresolved_placeholder_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        output_dir = self.write_output(text + "\n{{short_answer}}\n")
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("placeholder" in error for error in errors), errors)

    def test_unknown_source_id_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        output_dir = self.write_output(text.replace("src_001", "src_missing", 1))
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("unknown source ids" in error for error in errors), errors)

    def test_missing_source_table_row_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        output_dir = self.write_output(
            text.replace(
                "| src_001 | A | Official game-regulation source placeholder | Placeholder article | Placeholder pinpoint |\n",
                "",
            )
        )
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("missing metadata source rows" in error for error in errors), errors)

    def test_source_table_grade_mismatch_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        output_dir = self.write_output(
            text.replace(
                "| src_001 | A | Official game-regulation source placeholder | Placeholder article | Placeholder pinpoint |",
                "| src_001 | B | Official game-regulation source placeholder | Placeholder article | Placeholder pinpoint |",
            )
        )
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("grade mismatch" in error for error in errors), errors)

    def test_source_table_detail_mismatch_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        output_dir = self.write_output(
            text.replace(
                "| src_001 | A | Official game-regulation source placeholder | Placeholder article | Placeholder pinpoint |",
                "| src_001 | A | Different source title | Placeholder article | Placeholder pinpoint |",
            )
        )
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("detail mismatch" in error for error in errors), errors)

    def test_source_table_blank_cell_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        output_dir = self.write_output(
            text.replace(
                "| src_001 | A | Official game-regulation source placeholder | Placeholder article | Placeholder pinpoint |",
                "| src_001 | A | Official game-regulation source placeholder |  | Placeholder pinpoint |",
            )
        )
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("src_001.citation is empty" in error for error in errors), errors)

    def test_issue_block_missing_authority_source_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        output_dir = self.write_output(text.replace("- Sources: src_001", "- Sources:"))
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("missing authority source ids" in error for error in errors), errors)

    def test_route_context_research_mode_mismatch_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        output_dir = self.write_output(text.replace("- Research mode: `game_regulation`", "- Research mode: `general`"))
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("Research mode mismatch" in error for error in errors), errors)

    def test_route_context_co_running_agents_mismatch_fails(self) -> None:
        text = (VALID_OUTPUT / "legal-research-agent-result.md").read_text(encoding="utf-8")
        meta = valid_meta()
        meta["co_running_agents"] = ["pipa-specialist"]
        output_dir = self.write_output(text, meta=meta)
        errors = CHECKER.check_result_structure(output_dir)
        self.assertTrue(any("Co-running agents mismatch" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
