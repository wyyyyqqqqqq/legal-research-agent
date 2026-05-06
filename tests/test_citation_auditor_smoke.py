#!/usr/bin/env python3
"""Unit tests for deterministic citation-auditor smoke checks."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SMOKE_PATH = ROOT / "scripts" / "check-citation-auditor-smoke.py"


def load_smoke_checker():
    spec = importlib.util.spec_from_file_location("check_citation_auditor_smoke", SMOKE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load check-citation-auditor-smoke.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SMOKE = load_smoke_checker()


class CitationAuditorSmokeTest(unittest.TestCase):
    def test_repository_fixture_passes_smoke(self) -> None:
        self.assertEqual(SMOKE.run_smoke(), [])

    def test_missing_claim_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result_path = Path(temp_dir) / "result.md"
            result_path.write_text("# Result\n\nNo matching citation sentence here.\n", encoding="utf-8")

            errors = SMOKE.run_smoke(result_path, claim_text="Missing legal citation claim.")
            self.assertTrue(any("smoke claim not found" in error for error in errors), errors)

    def test_missing_result_fixture_is_reported(self) -> None:
        errors = SMOKE.run_smoke(Path("/tmp/nonexistent-citation-auditor-smoke-result.md"))
        self.assertTrue(any("missing result fixture" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
