#!/usr/bin/env python3
"""Unit tests for orchestrator intake payload validation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate-intake-payload.py"
PAYLOAD_DIR = ROOT / "tests" / "fixtures" / "intake-payloads"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_intake_payload", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load validate-intake-payload.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_validator()


def valid_payload() -> dict:
    return {
        "user_question": "한국에서 모바일 게임 확률형 아이템 규제를 조사해줘.",
        "output_dir": "/tmp/legal-research-agent",
        "active_profile": "merged",
        "orchestrator_classification": {
            "domains": ["game_regulation"],
            "jurisdictions": ["KR"],
            "route_mode": "game_regulation",
            "agent_research_mode": "game_regulation",
            "confidence": "high",
        },
        "co_running_agents": [],
        "style_guide_path": None,
    }


class IntakePayloadTest(unittest.TestCase):
    def test_valid_payload_passes(self) -> None:
        self.assertEqual(VALIDATOR.validate_payload(valid_payload()), [])

    def test_missing_classification_fails_by_default(self) -> None:
        payload = valid_payload()
        del payload["orchestrator_classification"]
        errors = VALIDATOR.validate_payload(payload)
        self.assertTrue(any("orchestrator_classification: missing" in error for error in errors), errors)

    def test_missing_classification_can_be_allowed_for_self_classification(self) -> None:
        payload = valid_payload()
        del payload["orchestrator_classification"]
        self.assertEqual(VALIDATOR.validate_payload(payload, allow_self_classified=True), [])

    def test_composite_route_requires_agent_research_mode(self) -> None:
        payload = valid_payload()
        payload["orchestrator_classification"]["route_mode"] = "game_and_data_protection"
        del payload["orchestrator_classification"]["agent_research_mode"]
        payload["orchestrator_classification"]["domains"] = ["game_regulation", "data_protection"]
        payload["co_running_agents"] = ["pipa-specialist"]
        errors = VALIDATOR.validate_payload(payload)
        self.assertTrue(any("composite route_mode requires" in error for error in errors), errors)

    def test_data_protection_composite_requires_co_running_agent(self) -> None:
        payload = valid_payload()
        payload["orchestrator_classification"]["route_mode"] = "game_and_data_protection"
        payload["orchestrator_classification"]["domains"] = ["game_regulation", "data_protection"]
        payload["co_running_agents"] = []
        errors = VALIDATOR.validate_payload(payload)
        self.assertTrue(any("co_running_agents: required" in error for error in errors), errors)

    def test_canonical_route_and_agent_mode_must_match(self) -> None:
        payload = valid_payload()
        payload["orchestrator_classification"]["route_mode"] = "general"
        payload["orchestrator_classification"]["agent_research_mode"] = "game_regulation"
        errors = VALIDATOR.validate_payload(payload)
        self.assertTrue(any("must match" in error for error in errors), errors)

    def test_legacy_agent_ids_are_rejected(self) -> None:
        payload = valid_payload()
        payload["co_running_agents"] = ["general-legal-research"]
        errors = VALIDATOR.validate_payload(payload)
        self.assertTrue(any("legacy agent" in error for error in errors), errors)

    def test_duplicate_canonical_agent_in_selected_agents_fails(self) -> None:
        payload = valid_payload()
        payload["selected_agents"] = ["legal-research-agent", "legal-research-agent"]
        errors = VALIDATOR.validate_payload(payload)
        self.assertTrue(any("must be deduplicated" in error for error in errors), errors)

    def test_repository_payload_fixtures_pass(self) -> None:
        result = VALIDATOR.validate_paths([PAYLOAD_DIR])
        self.assertEqual(result["status"], "pass", result)
        self.assertGreaterEqual(result["passed"], 4)

    def test_validate_paths_reports_json_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bad.json"
            path.write_text("{", encoding="utf-8")
            result = VALIDATOR.validate_paths([path])
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("json:" in error for error in result["results"][0]["errors"]))


if __name__ == "__main__":
    unittest.main()
