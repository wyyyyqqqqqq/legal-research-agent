#!/usr/bin/env python3
"""Unit tests for standalone deliverable workflow validation."""

from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts" / "check-standalone-workflow.py"
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "standalone-workflow"
CASE_FIXTURE = FIXTURE_ROOT / "kr-loot-box"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_standalone_workflow", CHECKER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-standalone-workflow.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_checker()


class StandaloneWorkflowTest(unittest.TestCase):
    def test_fixture_root_passes(self) -> None:
        self.assertEqual(CHECKER.validate_root(FIXTURE_ROOT), [])

    def test_manifest_file_passes(self) -> None:
        self.assertEqual(CHECKER.validate_root(CASE_FIXTURE / "standalone-deliverable-manifest.json"), [])

    def test_bad_filename_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copytree(CASE_FIXTURE, temp_path / "case")
            manifest_path = temp_path / "case" / "standalone-deliverable-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["deliverables"][0]["path"] = "deliverables/bad_name.md"
            (temp_path / "case" / "deliverables" / "bad_name.md").write_text(
                (CASE_FIXTURE / "deliverables" / "20260506_kr-loot-box-probability_standalone_ko_v1.md").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            errors = CHECKER.validate_root(temp_path / "case")
        self.assertTrue(any("filename does not match" in error for error in errors), errors)

    def test_missing_audit_claim_fails_for_deterministic_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copytree(CASE_FIXTURE, temp_path / "case")
            manifest_path = temp_path / "case" / "standalone-deliverable-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["deliverables"][0]["audit"]["claim"] = ""
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            errors = CHECKER.validate_root(temp_path / "case")
        self.assertTrue(any("audit.claim is required" in error for error in errors), errors)

    def test_missing_docx_object_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copytree(CASE_FIXTURE, temp_path / "case")
            manifest_path = temp_path / "case" / "standalone-deliverable-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            del manifest["deliverables"][0]["docx"]
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            errors = CHECKER.validate_root(temp_path / "case")
        self.assertTrue(any("docx object is required" in error for error in errors), errors)

    def test_generated_docx_status_requires_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copytree(CASE_FIXTURE, temp_path / "case")
            manifest_path = temp_path / "case" / "standalone-deliverable-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["deliverables"][0]["docx"] = {
                "status": "generated",
                "path": None,
                "render_report_path": None,
            }
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            errors = CHECKER.validate_root(temp_path / "case")
        self.assertTrue(any("docx.path is required" in error for error in errors), errors)

    def test_failed_live_audit_blocks_required_deliverable(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            shutil.copytree(CASE_FIXTURE, temp_path / "case")
            manifest_path = temp_path / "case" / "standalone-deliverable-manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["deliverables"][0]["audit"] = {
                "required": True,
                "status": "live_failed",
                "report_path": "deliverables/report.audit.md",
            }
            manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            errors = CHECKER.validate_root(temp_path / "case")
        self.assertTrue(any("blocking status" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
