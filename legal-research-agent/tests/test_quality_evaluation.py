#!/usr/bin/env python3
"""Unit tests for legal output quality evaluation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = ROOT / "scripts" / "evaluate-quality.py"
QUALITY_SPEC = ROOT / "tests" / "fixtures" / "quality" / "kr_loot_box-quality-spec.json"
VALID_OUTPUT = ROOT / "tests" / "fixtures" / "output" / "valid"


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluate_quality", EVALUATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load evaluate-quality.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EVALUATOR = load_evaluator()


def valid_meta() -> dict:
    return json.loads((VALID_OUTPUT / "legal-research-agent-meta.json").read_text(encoding="utf-8"))


class QualityEvaluationTest(unittest.TestCase):
    def write_output(self, meta: dict, result_text: str = "Official source verification is required.") -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "legal-research-agent-result.md").write_text(result_text, encoding="utf-8")
        (temp_dir / "legal-research-agent-meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return temp_dir

    def test_valid_sample_passes_quality_gate(self) -> None:
        spec = json.loads(QUALITY_SPEC.read_text(encoding="utf-8"))
        result = EVALUATOR.evaluate_output(VALID_OUTPUT, spec)
        self.assertEqual(result["status"], "pass", result)

    def test_high_confidence_c_only_fails(self) -> None:
        meta = valid_meta()
        meta["sources"][0]["grade"] = "C"
        meta["issue_map"][0]["confidence"] = "high"
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(output_dir)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("high-confidence" in error for error in result["errors"]))

    def test_error_output_blocks_high_confidence(self) -> None:
        meta = valid_meta()
        meta["issue_map"][0]["confidence"] = "high"
        meta["error"] = "source_coverage_insufficient"
        meta["coverage_gaps"] = [
            {
                "type": "source_coverage",
                "description": "Current official source coverage is incomplete.",
            }
        ]
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(output_dir)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("confidence_alignment" in error for error in result["errors"]))

    def test_fallback_output_blocks_high_confidence(self) -> None:
        meta = valid_meta()
        meta["research_mode"] = "fallback"
        meta["fallback_reason"] = "source_coverage_insufficient"
        meta["issue_map"][0]["confidence"] = "high"
        meta["issue_map"][0]["answer"] = "Only a conservative fallback answer is available."
        meta["error"] = "source_coverage_insufficient"
        meta["coverage_gaps"] = [
            {
                "type": "source_coverage",
                "description": "Current official source coverage is incomplete.",
            }
        ]
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(output_dir)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("confidence_alignment" in error for error in result["errors"]))

    def test_specialist_handoff_gap_does_not_automatically_block_high_confidence(self) -> None:
        meta = valid_meta()
        meta["issue_map"][0]["confidence"] = "high"
        meta["coverage_gaps"] = [
            {
                "type": "specialist_handoff",
                "description": "Privacy analysis is delegated to a co-running specialist.",
            }
        ]
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(output_dir)
        self.assertFalse(any("confidence_alignment" in error for error in result["errors"]))

    def test_d_grade_legal_basis_fails(self) -> None:
        meta = valid_meta()
        meta["sources"][0]["grade"] = "D"
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(output_dir)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("D-grade" in error for error in result["errors"]))

    def test_missing_required_jurisdiction_fails_against_case_spec(self) -> None:
        meta = valid_meta()
        meta["jurisdictions"] = ["JP"]
        output_dir = self.write_output(meta)
        spec = json.loads(QUALITY_SPEC.read_text(encoding="utf-8"))
        result = EVALUATOR.evaluate_output(output_dir, spec)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("jurisdiction_coverage" in error for error in result["errors"]))

    def test_missing_material_issue_term_fails_against_case_spec(self) -> None:
        meta = valid_meta()
        meta["issue_map"][0]["issue"] = "Generic issue"
        meta["issue_map"][0]["answer"] = "Generic answer"
        meta["summary"] = "Generic summary."
        meta["key_findings"] = ["Generic finding."]
        output_dir = self.write_output(meta, result_text="Official source verification is required.")
        spec = json.loads(QUALITY_SPEC.read_text(encoding="utf-8"))
        result = EVALUATOR.evaluate_output(output_dir, spec)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("material_issue_terms" in error for error in result["errors"]))

    def test_missing_required_comparison_matrix_fails(self) -> None:
        meta = valid_meta()
        meta["comparison_matrix"] = []
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(output_dir, {"requires_comparison_matrix": True})
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("comparison_matrix" in error for error in result["errors"]))

    def test_comparison_matrix_missing_required_jurisdiction_fails(self) -> None:
        meta = valid_meta()
        meta["jurisdictions"] = ["KR", "JP"]
        meta["comparison_matrix"] = [
            {
                "issue": "Classification",
                "KR": "Verify Korean classification requirements.",
                "status": "requires_current_source_check",
            }
        ]
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(
            output_dir,
            {
                "requires_comparison_matrix": True,
                "required_jurisdictions": ["KR", "JP"],
            },
        )
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("missing jurisdiction column 'JP'" in error for error in result["errors"]))

    def test_comparison_matrix_blank_issue_or_status_fails(self) -> None:
        meta = valid_meta()
        meta["jurisdictions"] = ["KR", "JP"]
        meta["comparison_matrix"] = [
            {
                "issue": "",
                "KR": "Verify Korean classification requirements.",
                "JP": "Verify Japanese classification requirements.",
                "status": "",
            }
        ]
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(
            output_dir,
            {
                "requires_comparison_matrix": True,
                "required_jurisdictions": ["KR", "JP"],
            },
        )
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any(".issue" in error for error in result["errors"]))
        self.assertTrue(any(".status" in error for error in result["errors"]))

    def test_missing_privacy_handoff_fails_when_required(self) -> None:
        meta = valid_meta()
        meta["co_running_agents"] = []
        output_dir = self.write_output(meta, result_text="Privacy is mentioned without ownership.")
        result = EVALUATOR.evaluate_output(output_dir, {"requires_privacy_handoff": True})
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("privacy_handoff" in error for error in result["errors"]))

    def test_missing_required_classification_warning_fails(self) -> None:
        meta = valid_meta()
        meta["classification_warnings"] = []
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(
            output_dir,
            {"required_classification_warnings": ["classification_mismatch"]},
        )
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("classification_warnings" in error for error in result["errors"]))

    def test_expected_error_fails_when_metadata_error_differs(self) -> None:
        meta = valid_meta()
        meta["error"] = None
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(output_dir, {"expected_error": "classification_mismatch"})
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any(error.startswith("error:") for error in result["errors"]))

    def test_missing_required_coverage_gap_type_fails(self) -> None:
        meta = valid_meta()
        meta["coverage_gaps"] = [
            {
                "type": "other",
                "description": "A non-specific gap.",
            }
        ]
        output_dir = self.write_output(meta)
        result = EVALUATOR.evaluate_output(
            output_dir,
            {"required_coverage_gap_types": ["classification_mismatch"]},
        )
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("coverage_gaps" in error for error in result["errors"]))

    def test_missing_required_taxonomy_fails(self) -> None:
        result = EVALUATOR.evaluate_output(
            VALID_OUTPUT,
            {"required_taxonomy": ["Platform and Distribution"]},
        )
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("taxonomy_coverage" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
