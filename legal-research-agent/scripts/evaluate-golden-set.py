#!/usr/bin/env python3
"""Run deterministic quality evaluation for a directory of golden-set outputs."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = ROOT / "scripts" / "evaluate-quality.py"
DEFAULT_OUTPUTS_ROOT = ROOT / "tests" / "fixtures" / "golden-set"
DEFAULT_SPEC_DIR = ROOT / "tests" / "fixtures" / "quality"
PASS = "pass"
FAIL = "fail"


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluate_quality", EVALUATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load evaluate-quality.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


EVALUATOR = load_evaluator()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fallback_case_id(path: Path) -> str:
    suffix = "-quality-spec.json"
    if path.name.endswith(suffix):
        return path.name[: -len(suffix)]
    return path.stem


def load_case_specs(spec_dir: Path) -> list[dict[str, Any]]:
    if not spec_dir.exists():
        raise FileNotFoundError(f"quality spec directory does not exist: {spec_dir}")

    spec_paths = sorted(spec_dir.glob("*-quality-spec.json"))
    if not spec_paths:
        raise FileNotFoundError(f"no quality specs found in {spec_dir}")

    cases: list[dict[str, Any]] = []
    seen: set[str] = set()
    for path in spec_paths:
        spec = load_json(path)
        if not isinstance(spec, dict):
            raise ValueError(f"{path}: quality spec must be a JSON object")
        case_id = str(spec.get("case_id") or fallback_case_id(path)).strip()
        if not case_id:
            raise ValueError(f"{path}: case_id must not be empty")
        if case_id in seen:
            raise ValueError(f"{path}: duplicate case_id {case_id!r}")
        seen.add(case_id)
        cases.append({"case_id": case_id, "spec_path": path, "spec": spec})
    return cases


def missing_output_result(case_id: str, output_dir: Path) -> dict[str, Any]:
    return {
        "status": FAIL,
        "errors": [f"missing_output_dir: {output_dir}"],
        "warnings": [],
        "checks": {},
        "case_id": case_id,
    }


def evaluate_golden_set(
    outputs_root: Path = DEFAULT_OUTPUTS_ROOT,
    spec_dir: Path = DEFAULT_SPEC_DIR,
    case_ids: set[str] | None = None,
) -> dict[str, Any]:
    cases = load_case_specs(spec_dir)
    requested = case_ids or set()
    results: list[dict[str, Any]] = []
    found: set[str] = set()

    for case in cases:
        case_id = case["case_id"]
        if requested and case_id not in requested:
            continue
        found.add(case_id)
        output_dir = outputs_root / case_id
        if output_dir.exists():
            result = EVALUATOR.evaluate_output(output_dir, case["spec"])
        else:
            result = missing_output_result(case_id, output_dir)
        result["case_id"] = case_id
        result["spec_id"] = case["spec"].get("id")
        result["spec_path"] = str(case["spec_path"])
        result["output_dir"] = str(output_dir)
        results.append(result)

    for missing_case_id in sorted(requested - found):
        output_dir = outputs_root / missing_case_id
        result = missing_output_result(missing_case_id, output_dir)
        result["spec_id"] = None
        result["spec_path"] = None
        result["output_dir"] = str(output_dir)
        result["errors"].insert(0, f"unknown_case_id: {missing_case_id}")
        results.append(result)

    total = len(results)
    failed = sum(1 for result in results if result["status"] == FAIL)
    warned = sum(1 for result in results if result.get("warnings"))
    passed = total - failed
    status = PASS if total > 0 and failed == 0 else FAIL
    return {
        "status": status,
        "total": total,
        "passed": passed,
        "failed": failed,
        "warned": warned,
        "outputs_root": str(outputs_root),
        "spec_dir": str(spec_dir),
        "cases": results,
    }


def print_text_report(result: dict[str, Any]) -> None:
    print(f"Golden-set: {result['status'].upper()} ({result['passed']}/{result['total']} passed)")
    for case in result["cases"]:
        print(f"- {case['case_id']}: {case['status'].upper()}")
        for error in case.get("errors", []):
            print(f"  FAIL: {error}")
        for warning in case.get("warnings", []):
            print(f"  WARN: {warning}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outputs-root", type=Path, default=DEFAULT_OUTPUTS_ROOT)
    parser.add_argument("--quality-spec-dir", type=Path, default=DEFAULT_SPEC_DIR)
    parser.add_argument("--case-id", action="append", default=[], help="Limit evaluation to one case id.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    args = parser.parse_args(argv)

    try:
        result = evaluate_golden_set(
            outputs_root=args.outputs_root,
            spec_dir=args.quality_spec_dir,
            case_ids=set(args.case_id) if args.case_id else None,
        )
    except Exception as exc:
        if args.json:
            print(json.dumps({"status": FAIL, "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_text_report(result)

    return 0 if result["status"] == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
