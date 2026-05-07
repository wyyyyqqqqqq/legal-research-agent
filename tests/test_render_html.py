#!/usr/bin/env python3
"""Validate render-html.py output structure on a fixture."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "render-html.py"
INPUT_FIXTURE = (
    REPO_ROOT / "tests" / "fixtures" / "render-html" / "sample-input.md"
)


class RenderHtmlTest(unittest.TestCase):
    def test_renders_with_expected_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out.html"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(INPUT_FIXTURE), str(output)],
                cwd=REPO_ROOT, capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0,
                             msg=result.stdout + result.stderr)
            self.assertTrue(output.exists())
            html = output.read_text(encoding="utf-8")

        for marker in (
            "<!DOCTYPE html>",
            "<title>",
            "<h1>Test Title</h1>",
            "<h2>Scope and As-of Date</h2>",
            "<h2>Conclusion</h2>",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, html)


if __name__ == "__main__":
    unittest.main()
