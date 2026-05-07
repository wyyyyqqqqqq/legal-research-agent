#!/usr/bin/env python3
"""Validate output-mode templates, frameworks, fixtures, and the parity
of REQUIRED_OUTPUT_MODE_SECTIONS between the two scripts that maintain it."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_OUTPUT_MODES = REPO_ROOT / "scripts" / "check-output-modes.py"
CHECK_FORMATTER_OUTPUT = REPO_ROOT / "scripts" / "check-formatter-output.py"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECK_OUTPUT_MODES_MODULE = _load_module(
    "check_output_modes", CHECK_OUTPUT_MODES
)
CHECK_FORMATTER_OUTPUT_MODULE = _load_module(
    "check_formatter_output", CHECK_FORMATTER_OUTPUT
)


class OutputModesTest(unittest.TestCase):
    def test_templates_and_frameworks_valid(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CHECK_OUTPUT_MODES)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    def test_each_fixture_passes_mode_aware_formatter_check(self) -> None:
        modes = [
            ("executive-brief", "executive_brief"),
            ("comparative-matrix", "comparative_matrix"),
            ("enforcement-case-law", "enforcement_case_law"),
            ("black-letter-commentary", "black_letter_commentary"),
        ]
        for fixture_dir, slug in modes:
            with self.subTest(slug=slug):
                base = REPO_ROOT / "tests" / "fixtures" / "output-modes" / fixture_dir
                result = subprocess.run(
                    [
                        sys.executable,
                        str(CHECK_FORMATTER_OUTPUT),
                        str(base / "deliverable.md"),
                        "--meta",
                        str(base / "legal-research-agent-meta.json"),
                        "--language",
                        "en",
                        "--output-mode",
                        slug,
                    ],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    msg=(
                        f"slug={slug}\n"
                        f"stdout:\n{result.stdout}\n"
                        f"stderr:\n{result.stderr}"
                    ),
                )

    def test_required_section_parity_between_scripts(self) -> None:
        """REQUIRED_OUTPUT_MODE_SECTIONS in check-output-modes.py and
        check-formatter-output.py must agree section-for-section."""
        framework_view = CHECK_OUTPUT_MODES_MODULE.REQUIRED_TEMPLATE_SECTIONS
        formatter_view = (
            CHECK_FORMATTER_OUTPUT_MODULE.REQUIRED_OUTPUT_MODE_SECTIONS
        )

        slug_to_template = {
            "executive_brief": "templates/output-modes/executive-brief.md",
            "comparative_matrix": "templates/output-modes/comparative-matrix.md",
            "enforcement_case_law": "templates/output-modes/enforcement-case-law.md",
            "black_letter_commentary": "templates/output-modes/black-letter-commentary.md",
        }

        self.assertEqual(set(formatter_view), set(slug_to_template))
        for slug, template_rel in slug_to_template.items():
            self.assertEqual(
                framework_view[template_rel],
                formatter_view[slug],
                msg=(
                    f"Drift detected for {slug!r}: "
                    f"check-output-modes.py expects "
                    f"{framework_view[template_rel]} but "
                    f"check-formatter-output.py expects {formatter_view[slug]}"
                ),
            )


if __name__ == "__main__":
    unittest.main()
