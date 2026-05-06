#!/usr/bin/env python3
"""Unit tests for the local output contract validator."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate-output.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_output", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load validate-output.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def valid_meta() -> dict:
    return {
        "meta_version": "1.1",
        "summary": "A valid summary.",
        "research_mode": "game_regulation",
        "mode_source": "orchestrator",
        "active_profile": "merged",
        "orchestrator_route_mode": "game_regulation",
        "fallback_reason": None,
        "classification_warnings": [],
        "co_running_agents": [],
        "jurisdictions": ["KR"],
        "domains": ["game_regulation"],
        "issue_map": [
            {
                "issue": "Probability disclosure",
                "answer": "Disclosure is required under the relevant game rules.",
                "authority_ids": ["src_001"],
                "confidence": "high",
            }
        ],
        "key_findings": ["Probability disclosure should be verified against official rules."],
        "sources": [
            {
                "id": "src_001",
                "title": "Official game regulation source",
                "grade": "A",
                "citation": "Article 1",
                "pinpoint": "Article 1",
                "url_or_access": "official source",
            }
        ],
        "comparison_matrix": [],
        "coverage_gaps": [],
        "error": None,
    }


class OutputContractTest(unittest.TestCase):
    def write_output(self, meta: dict) -> Path:
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "legal-research-agent-result.md").write_text("Result body", encoding="utf-8")
        (temp_dir / "legal-research-agent-meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return temp_dir

    def test_valid_output_passes(self) -> None:
        output_dir = self.write_output(valid_meta())
        warnings = VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")
        self.assertEqual(warnings, [])

    def test_unknown_authority_id_fails(self) -> None:
        meta = valid_meta()
        meta["issue_map"][0]["authority_ids"] = ["src_missing"]
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_source_detail_fields_must_be_non_empty(self) -> None:
        meta = valid_meta()
        meta["sources"][0]["citation"] = ""
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_source_url_or_access_is_required(self) -> None:
        meta = valid_meta()
        del meta["sources"][0]["url_or_access"]
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_summary_must_be_non_empty(self) -> None:
        meta = valid_meta()
        meta["summary"] = " "
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_summary_must_not_be_placeholder(self) -> None:
        meta = valid_meta()
        meta["summary"] = "TBD"
        output_dir = self.write_output(meta)
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "placeholder"):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_summary_must_fit_rough_token_limit(self) -> None:
        meta = valid_meta()
        meta["summary"] = "a" * ((VALIDATOR.SUMMARY_MAX_ROUGH_TOKENS * 4) + 1)
        output_dir = self.write_output(meta)
        with self.assertRaisesRegex(VALIDATOR.ValidationError, "rough-token limit"):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_route_metadata_strings_must_be_non_empty(self) -> None:
        meta = valid_meta()
        meta["active_profile"] = ""
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_jurisdictions_must_be_non_empty_string_list(self) -> None:
        meta = valid_meta()
        meta["jurisdictions"] = [""]
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_domains_must_be_non_empty_list(self) -> None:
        meta = valid_meta()
        meta["domains"] = []
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_issue_text_fields_must_be_non_empty(self) -> None:
        meta = valid_meta()
        meta["issue_map"][0]["answer"] = ""
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_authority_ids_must_be_non_empty_strings(self) -> None:
        meta = valid_meta()
        meta["issue_map"][0]["authority_ids"] = [""]
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_key_findings_items_must_be_non_empty_strings(self) -> None:
        meta = valid_meta()
        meta["key_findings"] = [" "]
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_fallback_requires_reason(self) -> None:
        meta = valid_meta()
        meta["research_mode"] = "fallback"
        meta["fallback_reason"] = None
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_classification_mismatch_requires_warning(self) -> None:
        meta = valid_meta()
        meta["error"] = "classification_mismatch"
        meta["classification_warnings"] = []
        meta["coverage_gaps"] = [
            {
                "type": "classification_mismatch",
                "description": "Route and question conflict.",
            }
        ]
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_error_requires_matching_coverage_gap_type(self) -> None:
        meta = valid_meta()
        meta["error"] = "source_coverage_insufficient"
        meta["coverage_gaps"] = [
            {
                "type": "other",
                "description": "A gap exists but has the wrong type.",
            }
        ]
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")

    def test_fallback_requires_coverage_gap(self) -> None:
        meta = valid_meta()
        meta["research_mode"] = "fallback"
        meta["fallback_reason"] = "source_coverage_insufficient"
        meta["error"] = "source_coverage_insufficient"
        meta["coverage_gaps"] = []
        output_dir = self.write_output(meta)
        with self.assertRaises(VALIDATOR.ValidationError):
            VALIDATOR.validate_output_dir(output_dir, "legal-research-agent")


if __name__ == "__main__":
    unittest.main()
