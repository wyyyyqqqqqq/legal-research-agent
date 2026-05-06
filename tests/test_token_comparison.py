#!/usr/bin/env python3
"""Unit tests for route-pattern token comparison."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPARER_PATH = ROOT / "scripts" / "compare-token-runs.py"
FIXTURE_MANIFEST = ROOT / "tests" / "fixtures" / "token-comparison" / "token-comparison-manifest.json"


def load_comparer():
    spec = importlib.util.spec_from_file_location("compare_token_runs", COMPARER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load compare-token-runs.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMPARER = load_comparer()


def manifest_data(patterns: list[dict], **overrides: object) -> dict:
    data: dict = {
        "version": "1.0",
        "patterns": patterns,
    }
    data.update(overrides)
    return data


def write_events(path: Path, input_tokens: int, output_tokens: int, cache_create: int = 0) -> None:
    path.write_text(
        json.dumps(
            {
                "type": "message",
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "cache_creation_input_tokens": cache_create,
                    "cache_read_input_tokens": 0,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )


class TokenComparisonTest(unittest.TestCase):
    def test_fixture_manifest_passes_with_actual_token_savings(self) -> None:
        result = COMPARER.compare_manifest(FIXTURE_MANIFEST)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["failed"], 0)
        decisions = {pattern["route_pattern"]: pattern["decision"] for pattern in result["patterns"]}
        self.assertEqual(decisions["general-only"], "token_savings")
        self.assertEqual(decisions["game-plus-general"], "token_savings")
        self.assertTrue(all(pattern["quality_report"] for pattern in result["patterns"]))
        self.assertEqual(result["manifest_version"], "1.0")
        self.assertEqual(result["required_route_patterns"], ["game-plus-general", "general-only"])
        self.assertEqual(result["summary"]["decision_counts"], {"token_savings": 2})
        self.assertEqual(result["summary"]["actual_tokens"]["patterns"], 2)
        self.assertTrue(result["summary"]["actual_tokens"]["complete"])
        self.assertEqual(result["summary"]["actual_tokens"]["legacy"]["total_billed_like"], 1180)
        self.assertEqual(result["summary"]["actual_tokens"]["merged"]["total_billed_like"], 775)
        self.assertEqual(result["summary"]["actual_tokens"]["delta"]["total_billed_like"], -405)
        self.assertEqual(result["summary"]["actual_tokens"]["delta"]["percent"], -34.32)
        self.assertEqual(result["summary"]["agent_calls"]["delta"], -1)
        self.assertTrue(result["summary"]["agent_calls"]["complete"])
        deltas = {pattern["route_pattern"]: pattern["delta"]["agent_calls"] for pattern in result["patterns"]}
        self.assertEqual(deltas["general-only"], 0)
        self.assertEqual(deltas["game-plus-general"], -1)

    def test_token_increase_without_quality_reason_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 100, 20)
            write_events(root / "merged.jsonl", 140, 30)
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "general-only",
                                "quality_status": "pass",
                                "legacy": {"events": ["legacy.jsonl"]},
                                "merged": {"events": ["merged.jsonl"]},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            result = COMPARER.compare_manifest(manifest)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["patterns"][0]["decision"], "blocked_token_increase")
        self.assertTrue(any("quality_reason" in error for error in result["patterns"][0]["errors"]))

    def test_token_increase_with_quality_reason_passes_for_review(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 100, 20)
            write_events(root / "merged.jsonl", 140, 30)
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "game-only",
                                "quality_status": "pass",
                                "quality_reason": "Merged run added controlling regulator guidance.",
                                "legacy": {"events": ["legacy.jsonl"]},
                                "merged": {"events": ["merged.jsonl"]},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            result = COMPARER.compare_manifest(manifest)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["patterns"][0]["decision"], "token_increase_with_quality_reason")

    def test_agent_call_increase_without_reason_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 100, 20)
            write_events(root / "merged.jsonl", 90, 20)
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "general-only",
                                "quality_status": "pass",
                                "legacy": {"events": ["legacy.jsonl"], "agent_calls": 2},
                                "merged": {"events": ["merged.jsonl"], "agent_calls": 3},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            result = COMPARER.compare_manifest(manifest)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["patterns"][0]["decision"], "blocked_agent_call_increase")
        self.assertEqual(result["patterns"][0]["delta"]["agent_calls"], 1)
        self.assertTrue(any("agent_calls" in error for error in result["patterns"][0]["errors"]))

    def test_agent_call_increase_with_reason_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 100, 20)
            write_events(root / "merged.jsonl", 90, 20)
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "game-plus-data-protection",
                                "quality_status": "pass",
                                "agent_call_reason": "Merged route intentionally retained a co-running privacy specialist.",
                                "legacy": {"events": ["legacy.jsonl"], "agent_calls": 2},
                                "merged": {"events": ["merged.jsonl"], "agent_calls": 3},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            result = COMPARER.compare_manifest(manifest)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["patterns"][0]["agent_call_reason"], "Merged route intentionally retained a co-running privacy specialist.")
        self.assertEqual(result["patterns"][0]["delta"]["agent_calls"], 1)

    def test_quality_failure_blocks_even_with_token_savings(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 200, 50)
            write_events(root / "merged.jsonl", 100, 20)
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "game-only",
                                "quality_status": "fail",
                                "legacy": {"events": ["legacy.jsonl"]},
                                "merged": {"events": ["merged.jsonl"]},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            result = COMPARER.compare_manifest(manifest)
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["patterns"][0]["decision"], "blocked_quality")

    def test_quality_report_status_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 200, 50)
            write_events(root / "merged.jsonl", 100, 20)
            quality_report = root / "quality.json"
            quality_report.write_text(
                json.dumps({"case_id": "case_a", "status": "fail"}),
                encoding="utf-8",
            )
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "case_id": "case_a",
                                "route_pattern": "general-only",
                                "quality_status": "pass",
                                "quality_report": "quality.json",
                                "legacy": {"events": ["legacy.jsonl"]},
                                "merged": {"events": ["merged.jsonl"]},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            result = COMPARER.compare_manifest(manifest)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("quality_report: status mismatch" in error for error in result["patterns"][0]["errors"]))

    def test_quality_report_case_id_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 200, 50)
            write_events(root / "merged.jsonl", 100, 20)
            quality_report = root / "quality.json"
            quality_report.write_text(
                json.dumps({"case_id": "different_case", "status": "pass"}),
                encoding="utf-8",
            )
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "case_id": "case_a",
                                "route_pattern": "general-only",
                                "quality_status": "pass",
                                "quality_report": "quality.json",
                                "legacy": {"events": ["legacy.jsonl"]},
                                "merged": {"events": ["merged.jsonl"]},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            result = COMPARER.compare_manifest(manifest)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("quality_report: case_id mismatch" in error for error in result["patterns"][0]["errors"]))

    def test_proxy_only_manifest_passes_with_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "fallback",
                                "quality_status": "pass",
                                "legacy": {"proxy_metrics": {"agent_calls": 3, "result_bytes": 1000}},
                                "merged": {"proxy_metrics": {"agent_calls": 2, "result_bytes": 800}},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            result = COMPARER.compare_manifest(manifest)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["patterns"][0]["decision"], "proxy_only_review")
        self.assertEqual(result["patterns"][0]["delta"]["agent_calls"], -1)
        self.assertEqual(result["patterns"][0]["delta"]["proxy_metrics"]["result_bytes"], -200)
        self.assertEqual(result["summary"]["actual_tokens"]["patterns"], 0)
        self.assertFalse(result["summary"]["actual_tokens"]["complete"])
        self.assertEqual(result["summary"]["proxy_only_patterns"], 1)
        self.assertEqual(result["summary"]["agent_calls"]["delta"], -1)
        self.assertTrue(result["patterns"][0]["warnings"])

    def test_proxy_metric_increase_is_reported_as_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "fallback",
                                "quality_status": "pass",
                                "legacy": {
                                    "proxy_metrics": {
                                        "agent_calls": 2,
                                        "result_bytes": 1000,
                                        "wall_clock_ms": 5000,
                                    }
                                },
                                "merged": {
                                    "proxy_metrics": {
                                        "agent_calls": 2,
                                        "result_bytes": 1200,
                                        "wall_clock_ms": 7000,
                                    }
                                },
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            result = COMPARER.compare_manifest(manifest)
        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["patterns"][0]["delta"]["proxy_metrics"]["result_bytes"], 200)
        self.assertEqual(result["patterns"][0]["delta"]["proxy_metrics"]["wall_clock_ms"], 2000)
        self.assertTrue(any("result_bytes" in warning for warning in result["patterns"][0]["warnings"]))
        self.assertTrue(any("wall_clock_ms" in warning for warning in result["patterns"][0]["warnings"]))

    def test_top_level_agent_calls_must_match_proxy_metrics_agent_calls(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 100, 20)
            write_events(root / "merged.jsonl", 90, 20)
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "general-only",
                                "quality_status": "pass",
                                "legacy": {
                                    "events": ["legacy.jsonl"],
                                    "agent_calls": 2,
                                    "proxy_metrics": {"agent_calls": 3},
                                },
                                "merged": {"events": ["merged.jsonl"], "agent_calls": 2},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(COMPARER.TokenComparisonError, "agent_calls mismatch"):
                COMPARER.compare_manifest(manifest)

    def test_missing_events_file_raises_manifest_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "general-only",
                                "quality_status": "pass",
                                "legacy": {"events": ["missing.jsonl"]},
                                "merged": {"proxy_metrics": {"agent_calls": 1}},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(COMPARER.TokenComparisonError, "does not exist"):
                COMPARER.compare_manifest(manifest)

    def test_manifest_version_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = Path(temp_dir) / "manifest.json"
            manifest.write_text(json.dumps({"patterns": []}), encoding="utf-8")
            with self.assertRaisesRegex(COMPARER.TokenComparisonError, "manifest.version"):
                COMPARER.compare_manifest(manifest)

    def test_required_route_pattern_must_be_present(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 100, 20)
            write_events(root / "merged.jsonl", 90, 20)
            manifest = root / "manifest.json"
            manifest.write_text(
                json.dumps(
                    manifest_data(
                        [
                            {
                                "route_pattern": "general-only",
                                "quality_status": "pass",
                                "legacy": {"events": ["legacy.jsonl"]},
                                "merged": {"events": ["merged.jsonl"]},
                            }
                        ],
                        required_route_patterns=["general-only", "game-only"],
                    )
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(COMPARER.TokenComparisonError, "required_route_patterns"):
                COMPARER.compare_manifest(manifest)

    def test_duplicate_case_id_fails_manifest_integrity(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            write_events(root / "legacy.jsonl", 100, 20)
            write_events(root / "merged.jsonl", 90, 20)
            pattern = {
                "case_id": "case_a",
                "route_pattern": "general-only",
                "quality_status": "pass",
                "legacy": {"events": ["legacy.jsonl"]},
                "merged": {"events": ["merged.jsonl"]},
            }
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps(manifest_data([pattern, pattern])), encoding="utf-8")
            with self.assertRaisesRegex(COMPARER.TokenComparisonError, "duplicates"):
                COMPARER.compare_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
