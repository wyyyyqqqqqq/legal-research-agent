#!/usr/bin/env python3
"""Validate user-config schema fixtures."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check-user-config.py"


def _run(config: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), "--config", str(config)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class UserConfigTest(unittest.TestCase):
    def test_skip_when_absent(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(CHECK_SCRIPT),
                "--config",
                "/nonexistent/user-config.json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("SKIP", result.stdout)

    def test_example_valid(self) -> None:
        result = _run(REPO_ROOT / "templates" / "user-config.example.json")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_valid_fixtures_pass(self) -> None:
        for name in (
            "kr-game-only.json",
            "kr-fintech-multi.json",
            "en-us-corporate.json",
        ):
            with self.subTest(fixture=name):
                result = _run(
                    REPO_ROOT / "tests" / "fixtures" / "user-config" / name
                )
                self.assertEqual(
                    result.returncode, 0, msg=result.stdout + result.stderr
                )

    def test_invalid_fixture_fails(self) -> None:
        result = _run(
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "user-config"
            / "invalid-missing-jurisdictions.json"
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("primary must be a non-empty list", result.stderr)

    def test_fixture_with_generated_dir_parses(self) -> None:
        """The kr-fintech-multi fixture carries a non-empty
        generated_knowledge_directories entry. Confirm it parses with
        the expected shape so future schema changes break this test
        deliberately."""
        import json

        fixture = (
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "user-config"
            / "kr-fintech-multi.json"
        )
        data = json.loads(fixture.read_text(encoding="utf-8"))
        entries = data["generated_knowledge_directories"]
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry["path"], "knowledge/fintech-regulatory/")
        self.assertEqual(entry["industry"], "fintech")
        self.assertEqual(entry["area_of_law"], "regulatory")
        self.assertEqual(entry["jurisdiction"], "KR")
        self.assertEqual(entry["review_status"], "draft")
        self.assertEqual(entry["source_audit_status"], "live_passed")
        self.assertIsNone(entry["lifted_at"])


if __name__ == "__main__":
    unittest.main()
