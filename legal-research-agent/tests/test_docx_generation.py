#!/usr/bin/env python3
"""Unit tests for standalone Markdown-to-DOCX generation."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from citation_auditor.docx import extract_docx

RENDERER_PATH = ROOT / "scripts" / "render-docx.py"
SMOKE_PATH = ROOT / "scripts" / "check-docx-generation.py"
FIXTURE_MD = (
    ROOT
    / "tests"
    / "fixtures"
    / "standalone-workflow"
    / "kr-loot-box"
    / "deliverables"
    / "20260506_kr-loot-box-probability_standalone_ko_v1.md"
)


def load_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RENDERER = load_module(RENDERER_PATH, "render_docx")
SMOKE = load_module(SMOKE_PATH, "check_docx_generation")


class DocxGenerationTest(unittest.TestCase):
    def test_docx_smoke_passes(self) -> None:
        self.assertEqual(SMOKE.run_smoke(), [])

    def test_render_docx_preserves_title_source_and_table_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_docx = Path(temp_dir) / "memo.docx"
            report_path = Path(temp_dir) / "memo.report.json"
            report = RENDERER.render_docx(
                FIXTURE_MD,
                output_docx,
                language="ko",
                jurisdiction="korea",
                classification="AI-generated research draft",
                report_path=report_path,
            )
            extracted, source_map = extract_docx(output_docx)
            report_exists = report_path.exists()

        self.assertGreater(report["output_bytes"], 0)
        self.assertGreaterEqual(report["tables"], 1)
        self.assertIn("한국 모바일 게임 확률형 아이템 표시의무 검토", extracted)
        self.assertIn("src_001", extracted)
        self.assertIn("Official game-regulation source placeholder", extracted)
        self.assertTrue(source_map.blocks)
        self.assertTrue(report_exists)

    def test_render_docx_refuses_overwrite_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_docx = Path(temp_dir) / "memo.docx"
            RENDERER.render_docx(FIXTURE_MD, output_docx, language="ko", jurisdiction="korea")
            with self.assertRaises(RENDERER.RenderError):
                RENDERER.render_docx(FIXTURE_MD, output_docx, language="ko", jurisdiction="korea")

    def test_render_docx_requires_docx_extension(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(RENDERER.RenderError):
                RENDERER.render_docx(
                    FIXTURE_MD,
                    Path(temp_dir) / "memo.txt",
                    language="ko",
                    jurisdiction="korea",
                )


if __name__ == "__main__":
    unittest.main()
