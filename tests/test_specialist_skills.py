#!/usr/bin/env python3
"""Validate specialist-skill catalog completeness."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check-specialist-skills.py"


class SpecialistSkillsTest(unittest.TestCase):
    def test_catalog_complete(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECK_SCRIPT)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode, 0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
