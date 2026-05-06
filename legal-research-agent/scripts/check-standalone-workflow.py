#!/usr/bin/env python3
"""Validate standalone deliverable workflow manifests and fixtures."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FORMATTER_CHECKER_PATH = ROOT / "scripts" / "check-formatter-output.py"
CITATION_SMOKE_PATH = ROOT / "scripts" / "check-citation-auditor-smoke.py"

DELIVERABLE_NAME_PATTERN = re.compile(
    r"^\d{8}_[a-z0-9][a-z0-9-]*_(standalone|handoff|docx-ready)_(ko|en|bilingual)_v[1-9]\d*\.md$"
)
MODE_TO_FILENAME_TOKEN = {
    "standalone_markdown": "standalone",
    "handoff_packet": "handoff",
    "docx_ready_markdown": "docx-ready",
}
AUDIT_STATUSES = {
    "not_required",
    "not_run_session_unavailable",
    "deterministic_smoke",
    "live_passed",
    "live_failed",
}
FINAL_BLOCKING_AUDIT_STATUSES = {"live_failed"}
DOCX_STATUSES = {"not_requested", "not_generated", "generated", "generated_and_extracted"}


def load_module(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


FORMATTER_CHECKER = load_module(FORMATTER_CHECKER_PATH, "check_formatter_output")
CITATION_SMOKE = load_module(CITATION_SMOKE_PATH, "check_citation_auditor_smoke")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def manifest_paths(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(root.rglob("standalone-deliverable-manifest.json"))


def validate_manifest(manifest_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        manifest = load_json(manifest_path)
    except json.JSONDecodeError as exc:
        return [f"{manifest_path}: invalid JSON: {exc}"]

    if not isinstance(manifest, dict):
        return [f"{manifest_path}: manifest must be a JSON object"]

    base_dir = manifest_path.parent
    if manifest.get("workflow_version") != "1.0":
        errors.append(f"{manifest_path}: workflow_version must be '1.0'")
    if not isinstance(manifest.get("case_id"), str) or not manifest["case_id"].strip():
        errors.append(f"{manifest_path}: case_id is required")

    research_output_dir = manifest.get("research_output_dir")
    if not isinstance(research_output_dir, str) or not research_output_dir:
        errors.append(f"{manifest_path}: research_output_dir is required")
        research_dir = base_dir
    else:
        research_dir = (base_dir / research_output_dir).resolve()
        if not research_dir.exists():
            errors.append(f"{manifest_path}: research_output_dir does not exist: {research_output_dir}")

    deliverables = manifest.get("deliverables")
    if not isinstance(deliverables, list) or not deliverables:
        errors.append(f"{manifest_path}: deliverables must be a non-empty list")
        return errors

    seen_paths: set[str] = set()
    for index, deliverable in enumerate(deliverables):
        prefix = f"{manifest_path}: deliverables[{index}]"
        if not isinstance(deliverable, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        errors.extend(validate_deliverable(prefix, base_dir, research_dir, deliverable, seen_paths))

    return errors


def validate_deliverable(
    prefix: str,
    base_dir: Path,
    research_dir: Path,
    deliverable: dict[str, Any],
    seen_paths: set[str],
) -> list[str]:
    errors: list[str] = []
    mode = deliverable.get("mode")
    language = deliverable.get("language")
    if mode not in MODE_TO_FILENAME_TOKEN:
        errors.append(f"{prefix}: invalid mode {mode!r}")
    if language not in {"ko", "en", "bilingual"}:
        errors.append(f"{prefix}: invalid language {language!r}")

    path_value = deliverable.get("path")
    if not isinstance(path_value, str) or not path_value:
        errors.append(f"{prefix}: path is required")
        return errors
    if path_value in seen_paths:
        errors.append(f"{prefix}: duplicate deliverable path {path_value!r}")
    seen_paths.add(path_value)

    deliverable_path = (base_dir / path_value).resolve()
    if not deliverable_path.exists():
        errors.append(f"{prefix}: deliverable file does not exist: {path_value}")
    else:
        errors.extend(validate_filename(prefix, deliverable_path.name, mode, language))

    meta_path = resolve_manifest_path(base_dir, research_dir, deliverable.get("meta_path"))
    result_path = resolve_manifest_path(base_dir, research_dir, deliverable.get("result_path"))
    if meta_path is None:
        errors.append(f"{prefix}: meta_path is required")
    elif not meta_path.exists():
        errors.append(f"{prefix}: meta_path does not exist: {deliverable.get('meta_path')}")
    if result_path is None:
        errors.append(f"{prefix}: result_path is required")
    elif not result_path.exists():
        errors.append(f"{prefix}: result_path does not exist: {deliverable.get('result_path')}")

    if (
        deliverable_path.exists()
        and meta_path is not None
        and meta_path.exists()
        and mode in MODE_TO_FILENAME_TOKEN
        and language in {"ko", "en"}
    ):
        formatter_errors = FORMATTER_CHECKER.validate_formatter_output(
            deliverable_path,
            meta_path,
            language=language,
            mode=mode,
        )
        errors.extend(f"{prefix}: formatter: {error}" for error in formatter_errors)

    audit = deliverable.get("audit")
    if not isinstance(audit, dict):
        errors.append(f"{prefix}: audit object is required")
    else:
        errors.extend(validate_audit(prefix, deliverable_path, audit))

    docx = deliverable.get("docx")
    if not isinstance(docx, dict):
        errors.append(f"{prefix}: docx object is required")
    else:
        errors.extend(validate_docx(prefix, base_dir, docx))

    return errors


def validate_filename(prefix: str, filename: str, mode: Any, language: Any) -> list[str]:
    errors: list[str] = []
    if not DELIVERABLE_NAME_PATTERN.fullmatch(filename):
        errors.append(f"{prefix}: deliverable filename does not match standalone naming rules: {filename}")
        return errors
    if mode in MODE_TO_FILENAME_TOKEN and f"_{MODE_TO_FILENAME_TOKEN[mode]}_" not in filename:
        errors.append(f"{prefix}: filename does not match mode {mode!r}")
    if language in {"ko", "en", "bilingual"} and f"_{language}_" not in filename:
        errors.append(f"{prefix}: filename does not match language {language!r}")
    return errors


def resolve_manifest_path(base_dir: Path, research_dir: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    base_candidate = (base_dir / candidate).resolve()
    if base_candidate.exists():
        return base_candidate
    return (research_dir / candidate).resolve()


def validate_audit(prefix: str, deliverable_path: Path, audit: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = audit.get("required")
    if not isinstance(required, bool):
        errors.append(f"{prefix}: audit.required must be boolean")

    status = audit.get("status")
    if status not in AUDIT_STATUSES:
        errors.append(f"{prefix}: invalid audit.status {status!r}")
    elif required is True and status == "not_required":
        errors.append(f"{prefix}: audit.status cannot be not_required when audit.required is true")
    elif required is True and status in FINAL_BLOCKING_AUDIT_STATUSES:
        errors.append(f"{prefix}: required audit has blocking status {status!r}")

    claim = audit.get("claim")
    if status == "deterministic_smoke":
        if not isinstance(claim, str) or not claim.strip():
            errors.append(f"{prefix}: audit.claim is required for deterministic_smoke")
        elif deliverable_path.exists():
            smoke_errors = CITATION_SMOKE.run_smoke(deliverable_path, claim)
            errors.extend(f"{prefix}: citation_smoke: {error}" for error in smoke_errors)

    if status in {"live_passed", "live_failed"}:
        report_path = audit.get("report_path")
        if not isinstance(report_path, str) or not report_path:
            errors.append(f"{prefix}: live audit status requires report_path")
    return errors


def validate_docx(prefix: str, base_dir: Path, docx: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    status = docx.get("status")
    if status not in DOCX_STATUSES:
        errors.append(f"{prefix}: invalid docx.status {status!r}")
        return errors

    path_value = docx.get("path")
    report_value = docx.get("render_report_path")
    if status in {"not_requested", "not_generated"}:
        return errors

    if not isinstance(path_value, str) or not path_value:
        errors.append(f"{prefix}: docx.path is required when docx.status is {status!r}")
    else:
        docx_path = (base_dir / path_value).resolve()
        if not docx_path.exists():
            errors.append(f"{prefix}: docx.path does not exist: {path_value}")
        elif docx_path.suffix.lower() != ".docx":
            errors.append(f"{prefix}: docx.path must end with .docx")

    if not isinstance(report_value, str) or not report_value:
        errors.append(f"{prefix}: docx.render_report_path is required when docx.status is {status!r}")
    else:
        report_path = (base_dir / report_value).resolve()
        if not report_path.exists():
            errors.append(f"{prefix}: docx.render_report_path does not exist: {report_value}")
    return errors


def validate_root(root: Path) -> list[str]:
    manifests = manifest_paths(root)
    if not manifests:
        return [f"standalone workflow: no standalone-deliverable-manifest.json found under {root}"]
    errors: list[str] = []
    for manifest_path in manifests:
        errors.extend(validate_manifest(manifest_path))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="manifest file or fixture root")
    args = parser.parse_args(argv)

    errors = validate_root(args.path)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: standalone workflow valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
