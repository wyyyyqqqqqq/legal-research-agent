#!/usr/bin/env python3
"""Validate legal_sources fixtures."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check-legal-sources.py"


def _run(registry: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--registry", str(registry)],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )


class LegalSourcesTest(unittest.TestCase):
    def test_actual_registry_valid(self) -> None:
        result = _run(REPO_ROOT / "legal_sources.yaml")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_valid_fixture(self) -> None:
        result = _run(REPO_ROOT / "tests" / "fixtures" / "legal-sources" / "valid.yaml")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_invalid_fixture_fails(self) -> None:
        result = _run(
            REPO_ROOT / "tests" / "fixtures" / "legal-sources"
            / "invalid-missing-jurisdiction.yaml"
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
