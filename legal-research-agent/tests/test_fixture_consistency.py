#!/usr/bin/env python3
"""Unit tests for fixture/spec/golden-set consistency."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts" / "check-fixture-consistency.py"
CASE_DIR = ROOT / "tests" / "fixtures" / "cases"
QUALITY_DIR = ROOT / "tests" / "fixtures" / "quality"
GOLDEN_DIR = ROOT / "tests" / "fixtures" / "golden-set"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_fixture_consistency", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-fixture-consistency.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class FixtureConsistencyTest(unittest.TestCase):
    def test_repository_fixtures_are_consistent(self) -> None:
        self.assertEqual(CHECKER.check_consistency(CASE_DIR, QUALITY_DIR, GOLDEN_DIR), [])

    def test_missing_quality_spec_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_dir = root / "cases"
            quality_dir = root / "quality"
            golden_dir = root / "golden-set"
            case_dir.mkdir()
            quality_dir.mkdir()
            (golden_dir / "case_a").mkdir(parents=True)
            write_json(
                case_dir / "case_a.json",
                {
                    "id": "case_a",
                    "expected_research_mode": "general",
                    "jurisdictions": ["KR"],
                    "domains": ["general"],
                },
            )
            (golden_dir / "case_a" / "legal-research-agent-result.md").write_text("result", encoding="utf-8")
            (golden_dir / "case_a" / "legal-research-agent-meta.json").write_text("{}", encoding="utf-8")

            errors = CHECKER.check_consistency(case_dir, quality_dir, golden_dir)
            self.assertTrue(any("missing quality spec" in error for error in errors), errors)

    def test_mode_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_dir = root / "cases"
            quality_dir = root / "quality"
            golden_dir = root / "golden-set"
            case_dir.mkdir()
            quality_dir.mkdir()
            (golden_dir / "case_a").mkdir(parents=True)
            write_json(
                case_dir / "case_a.json",
                {
                    "id": "case_a",
                    "expected_research_mode": "general",
                    "jurisdictions": ["KR"],
                    "domains": ["general"],
                },
            )
            write_json(
                quality_dir / "case_a-quality-spec.json",
                {
                    "id": "case_a_quality",
                    "case_id": "case_a",
                    "expected_research_mode": "game_regulation",
                    "required_jurisdictions": ["KR"],
                    "required_domains": ["general"],
                },
            )
            (golden_dir / "case_a" / "legal-research-agent-result.md").write_text("result", encoding="utf-8")
            (golden_dir / "case_a" / "legal-research-agent-meta.json").write_text("{}", encoding="utf-8")

            errors = CHECKER.check_consistency(case_dir, quality_dir, golden_dir)
            self.assertTrue(any("expected_research_mode mismatch" in error for error in errors), errors)

    def test_missing_taxonomy_in_quality_spec_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_dir = root / "cases"
            quality_dir = root / "quality"
            golden_dir = root / "golden-set"
            taxonomy_path = root / "issue-taxonomy.md"
            case_dir.mkdir()
            quality_dir.mkdir()
            (golden_dir / "case_a").mkdir(parents=True)
            taxonomy_path.write_text("## Randomized Rewards\n", encoding="utf-8")
            write_json(
                case_dir / "case_a.json",
                {
                    "id": "case_a",
                    "expected_research_mode": "game_regulation",
                    "jurisdictions": ["KR"],
                    "domains": ["game_regulation"],
                    "required_taxonomy": ["Randomized Rewards"],
                },
            )
            write_json(
                quality_dir / "case_a-quality-spec.json",
                {
                    "id": "case_a_quality",
                    "case_id": "case_a",
                    "expected_research_mode": "game_regulation",
                    "required_jurisdictions": ["KR"],
                    "required_domains": ["game_regulation"],
                },
            )
            (golden_dir / "case_a" / "legal-research-agent-result.md").write_text("result", encoding="utf-8")
            (golden_dir / "case_a" / "legal-research-agent-meta.json").write_text("{}", encoding="utf-8")

            errors = CHECKER.check_consistency(case_dir, quality_dir, golden_dir, taxonomy_path)
            self.assertTrue(any("required_taxonomy" in error for error in errors), errors)

    def test_missing_comparison_matrix_requirement_in_quality_spec_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_dir = root / "cases"
            quality_dir = root / "quality"
            golden_dir = root / "golden-set"
            case_dir.mkdir()
            quality_dir.mkdir()
            (golden_dir / "case_a").mkdir(parents=True)
            write_json(
                case_dir / "case_a.json",
                {
                    "id": "case_a",
                    "expected_research_mode": "game_regulation",
                    "jurisdictions": ["KR", "JP"],
                    "domains": ["game_regulation"],
                    "requires_comparison_matrix": True,
                },
            )
            write_json(
                quality_dir / "case_a-quality-spec.json",
                {
                    "id": "case_a_quality",
                    "case_id": "case_a",
                    "expected_research_mode": "game_regulation",
                    "required_jurisdictions": ["KR", "JP"],
                    "required_domains": ["game_regulation"],
                },
            )
            (golden_dir / "case_a" / "legal-research-agent-result.md").write_text("result", encoding="utf-8")
            (golden_dir / "case_a" / "legal-research-agent-meta.json").write_text("{}", encoding="utf-8")

            errors = CHECKER.check_consistency(case_dir, quality_dir, golden_dir)
            self.assertTrue(any("requires_comparison_matrix mismatch" in error for error in errors), errors)

    def test_golden_output_without_case_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            case_dir = root / "cases"
            quality_dir = root / "quality"
            golden_dir = root / "golden-set"
            case_dir.mkdir()
            quality_dir.mkdir()
            (golden_dir / "orphan").mkdir(parents=True)

            errors = CHECKER.check_consistency(case_dir, quality_dir, golden_dir)
            self.assertTrue(any("no matching case fixture" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
