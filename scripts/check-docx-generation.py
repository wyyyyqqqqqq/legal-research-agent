#!/usr/bin/env python3
"""Run a deterministic DOCX generation smoke test for standalone deliverables."""

from __future__ import annotations

import argparse
import importlib.util
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from citation_auditor.docx import extract_docx

RENDERER_PATH = ROOT / "scripts" / "render-docx.py"
DEFAULT_INPUT = (
    ROOT
    / "tests"
    / "fixtures"
    / "standalone-workflow"
    / "kr-loot-box"
    / "deliverables"
    / "20260506_kr-loot-box-probability_standalone_ko_v1.md"
)
DEFAULT_REQUIRED_TEXT = [
    "한국 모바일 게임 확률형 아이템 표시의무 검토",
    "src_001",
    "Official game-regulation source placeholder",
]


def load_renderer():
    spec = importlib.util.spec_from_file_location("render_docx", RENDERER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load renderer: {RENDERER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


RENDERER = load_renderer()


def run_smoke(input_md: Path = DEFAULT_INPUT, required_text: list[str] | None = None) -> list[str]:
    required = required_text or DEFAULT_REQUIRED_TEXT
    errors: list[str] = []
    if not input_md.exists():
        return [f"missing DOCX input fixture: {input_md}"]

    with tempfile.TemporaryDirectory() as temp_dir:
        output_docx = Path(temp_dir) / "rendered.docx"
        report_path = Path(temp_dir) / "rendered.report.json"
        try:
            report = RENDERER.render_docx(
                input_md,
                output_docx,
                language="ko",
                jurisdiction="korea",
                classification="AI-generated research draft",
                report_path=report_path,
            )
        except Exception as exc:
            return [f"DOCX render failed: {exc}"]

        if not output_docx.exists() or output_docx.stat().st_size == 0:
            errors.append("DOCX render did not produce a non-empty file")
        if not report_path.exists():
            errors.append("DOCX render did not write the requested report")
        if int(report.get("tables", 0)) < 1:
            errors.append("DOCX render report did not record any tables")

        try:
            extracted_text, source_map = extract_docx(output_docx)
        except Exception as exc:
            return [*errors, f"DOCX extraction failed: {exc}"]

        if not source_map.blocks:
            errors.append("DOCX extraction produced no source blocks")
        for item in required:
            if item not in extracted_text:
                errors.append(f"DOCX extracted text missing required text: {item!r}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--require", action="append", default=[])
    args = parser.parse_args(argv)

    errors = run_smoke(args.input, args.require or None)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("OK: DOCX generation smoke valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
