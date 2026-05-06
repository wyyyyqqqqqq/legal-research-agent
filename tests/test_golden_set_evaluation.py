#!/usr/bin/env python3
"""Unit tests for golden-set batch quality evaluation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GOLDEN_EVALUATOR_PATH = ROOT / "scripts" / "evaluate-golden-set.py"
OUTPUTS_ROOT = ROOT / "tests" / "fixtures" / "golden-set"
SPEC_DIR = ROOT / "tests" / "fixtures" / "quality"


def load_golden_evaluator():
    spec = importlib.util.spec_from_file_location("evaluate_golden_set", GOLDEN_EVALUATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load evaluate-golden-set.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GOLDEN_EVALUATOR = load_golden_evaluator()


class GoldenSetEvaluationTest(unittest.TestCase):
    def test_fixture_golden_set_passes(self) -> None:
        result = GOLDEN_EVALUATOR.evaluate_golden_set(OUTPUTS_ROOT, SPEC_DIR)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["total"], 7)
        self.assertEqual(result["failed"], 0)

    def test_missing_output_dir_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            spec_dir = Path(temp_dir) / "quality"
            outputs_root = Path(temp_dir) / "outputs"
            spec_dir.mkdir()
            outputs_root.mkdir()
            (spec_dir / "missing_case-quality-spec.json").write_text(
                json.dumps({"id": "missing_case_quality", "case_id": "missing_case"}, indent=2),
                encoding="utf-8",
            )

            result = GOLDEN_EVALUATOR.evaluate_golden_set(outputs_root, spec_dir)
            self.assertEqual(result["status"], "fail")
            self.assertEqual(result["failed"], 1)
            self.assertTrue(any("missing_output_dir" in error for error in result["cases"][0]["errors"]))

    def test_case_id_filter_runs_single_case(self) -> None:
        result = GOLDEN_EVALUATOR.evaluate_golden_set(
            OUTPUTS_ROOT,
            SPEC_DIR,
            case_ids={"kr_general_basic"},
        )
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["cases"][0]["case_id"], "kr_general_basic")


if __name__ == "__main__":
    unittest.main()
