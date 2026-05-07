#!/usr/bin/env python3
"""Validate generated-knowledge fixtures against the recipe validator."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPT = REPO_ROOT / "scripts" / "check-generated-knowledge.py"


def _run(*dirs: Path) -> subprocess.CompletedProcess:
    args = [sys.executable, str(CHECK_SCRIPT)]
    for d in dirs:
        args.extend(["--dir", str(d)])
    return subprocess.run(
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class GeneratedKnowledgeTest(unittest.TestCase):
    def test_skip_when_absent(self) -> None:
        # Use --root pointing at a path that has no knowledge/ subtree.
        result = subprocess.run(
            [
                sys.executable,
                str(CHECK_SCRIPT),
                "--root",
                "/nonexistent/legal-research-agent",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode, 0, msg=result.stdout + result.stderr
        )
        self.assertIn("SKIP", result.stdout)

    def test_valid_fixture_passes(self) -> None:
        fixture = (
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "generated-knowledge"
            / "kr-fintech-regulatory"
        )
        result = _run(fixture)
        self.assertEqual(
            result.returncode, 0, msg=result.stdout + result.stderr
        )

    def test_missing_banner_fixture_fails(self) -> None:
        fixture = (
            REPO_ROOT
            / "tests"
            / "fixtures"
            / "generated-knowledge"
            / "invalid-missing-banner"
        )
        result = _run(fixture)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing or wrong banner", result.stderr)

    def test_recipe_doc_lists_all_required_files(self) -> None:
        """The recipe document must enumerate the four required Markdown
        files plus review-status.json so contributors and the wizard
        agree on the file set."""
        recipe = REPO_ROOT / "docs" / "knowledge-construction-recipe.md"
        text = recipe.read_text(encoding="utf-8")
        for required in (
            "issue-taxonomy.md",
            "regulatory-map.md",
            "source-map.md",
            "library-index.md",
            "review-status.json",
        ):
            with self.subTest(file=required):
                self.assertIn(required, text)


if __name__ == "__main__":
    unittest.main()
