#!/usr/bin/env python3
"""Unit tests for prompt-footprint measurement."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MEASURER_PATH = ROOT / "scripts" / "measure-prompt-footprint.py"


def load_measurer():
    spec = importlib.util.spec_from_file_location("measure_prompt_footprint", MEASURER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load measure-prompt-footprint.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MEASURER = load_measurer()


class PromptFootprintTest(unittest.TestCase):
    def test_rough_token_count_is_stable_char_proxy(self) -> None:
        self.assertEqual(MEASURER.rough_token_count(""), 0)
        self.assertEqual(MEASURER.rough_token_count("abcd"), 1)
        self.assertEqual(MEASURER.rough_token_count("abcde"), 2)

    def test_core_summary_finds_agent_instruction_files(self) -> None:
        summary = MEASURER.summarize_root(ROOT)
        self.assertEqual(summary["profile"], "core")
        self.assertGreater(summary["totals"]["rough_tokens"], 0)
        self.assertIn("agent_prompt", summary["by_category"])
        self.assertIn("skills", summary["by_category"])
        self.assertIn("knowledge", summary["by_category"])
        self.assertTrue(
            any(item["path"] == "CLAUDE.md" for item in summary["files"]),
            summary["files"],
        )

    def test_default_summary_excludes_vendored_claude_skills(self) -> None:
        summary = MEASURER.summarize_root(ROOT)
        self.assertFalse(any(item["path"].startswith(".claude/") for item in summary["files"]))

    def test_vendor_summary_can_include_vendored_claude_skills(self) -> None:
        summary = MEASURER.summarize_root(ROOT, include_vendor=True)
        self.assertEqual(summary["profile"], "core_plus_vendor")
        self.assertTrue(any(item["path"].startswith(".claude/") for item in summary["files"]))

    def test_temp_root_summary_counts_markdown_and_json_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "CLAUDE.md").write_text("abcd", encoding="utf-8")
            (root / "skills").mkdir()
            (root / "skills" / "one.md").write_text("alpha beta", encoding="utf-8")
            (root / "skills" / "ignore.txt").write_text("this should not count", encoding="utf-8")
            (root / "templates").mkdir()
            (root / "templates" / "meta.example.json").write_text('{"a": 1}', encoding="utf-8")

            summary = MEASURER.summarize_root(root)
            paths = [item["path"] for item in summary["files"]]
            self.assertEqual(paths, ["CLAUDE.md", "skills/one.md", "templates/meta.example.json"])
            self.assertEqual(summary["totals"]["files"], 3)


if __name__ == "__main__":
    unittest.main()
