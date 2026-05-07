#!/usr/bin/env python3
"""Validate /ingest skill and command structural surface."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class IngestStructureTest(unittest.TestCase):
    def test_skill_exists(self) -> None:
        path = REPO_ROOT / "skills" / "ingest.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        for required in (
            "## Workflow",
            "## Quality Floor",
            "## Fallback Gaps",
            "mcp__markitdown__",
            "Grade A / B / C",
        ):
            with self.subTest(marker=required):
                self.assertIn(required, text)

    def test_slash_command_exists(self) -> None:
        path = REPO_ROOT / ".claude" / "commands" / "ingest.md"
        self.assertTrue(path.exists())
        text = path.read_text(encoding="utf-8")
        self.assertIn("library/inbox/", text)

    def test_library_index_exists(self) -> None:
        path = REPO_ROOT / "library" / "_index.md"
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
