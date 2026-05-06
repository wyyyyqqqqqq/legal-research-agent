#!/usr/bin/env python3
"""Run the local legal-research-agent preflight checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "reports" / "local-checks-latest.json"


CHECKS: list[dict[str, Any]] = [
    {
        "id": "smoke_fixtures",
        "description": "Validate smoke case fixture shape.",
        "cmd": ["python3", "scripts/smoke-check.py"],
    },
    {
        "id": "fixture_consistency",
        "description": "Validate case/spec/golden-set fixture consistency.",
        "cmd": ["python3", "scripts/check-fixture-consistency.py"],
    },
    {
        "id": "intake_payloads",
        "description": "Validate orchestrator-to-agent intake payload fixtures.",
        "cmd": ["python3", "scripts/validate-intake-payload.py", "tests/fixtures/intake-payloads"],
    },
    {
        "id": "unit_tests",
        "description": "Run all local Python unit tests.",
        "cmd": ["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
    },
    {
        "id": "knowledge_coverage",
        "description": "Check that core source-planning markers remain present.",
        "cmd": ["python3", "scripts/check-knowledge-coverage.py"],
    },
    {
        "id": "prompt_footprint",
        "description": "Measure core prompt and instruction footprint.",
        "cmd": ["python3", "scripts/measure-prompt-footprint.py", "--json"],
    },
    {
        "id": "citation_auditor_vendor",
        "description": "Validate vendored citation-auditor files and CLI smoke.",
        "cmd": ["python3", "scripts/check-citation-auditor-vendor.py"],
    },
    {
        "id": "citation_auditor_smoke",
        "description": "Run deterministic citation-auditor chunk/aggregate/render smoke.",
        "cmd": ["python3", "scripts/check-citation-auditor-smoke.py"],
    },
    {
        "id": "output_contract",
        "description": "Validate sample output metadata contract.",
        "cmd": ["python3", "scripts/validate-output.py", "tests/fixtures/output/valid"],
    },
    {
        "id": "result_structure",
        "description": "Validate sample result memo structure.",
        "cmd": ["python3", "scripts/check-result-structure.py", "tests/fixtures/output/valid"],
    },
    {
        "id": "quality_gate",
        "description": "Run deterministic quality gate on sample output.",
        "cmd": [
            "python3",
            "scripts/evaluate-quality.py",
            "tests/fixtures/output/valid",
            "--case-spec",
            "tests/fixtures/quality/kr_loot_box-quality-spec.json",
            "--json",
        ],
    },
    {
        "id": "golden_set",
        "description": "Run deterministic golden-set batch evaluation.",
        "cmd": ["python3", "scripts/evaluate-golden-set.py", "--json"],
    },
    {
        "id": "legacy_invocation_lint",
        "description": "Ensure runtime files do not invoke legacy research agents.",
        "cmd": ["bash", "tests/lint_no_legacy_invocation.sh"],
    },
    {
        "id": "token_measurement",
        "description": "Verify token measurement parser against sample events.",
        "cmd": ["python3", "scripts/measure-tokens.py", "tests/fixtures/events/sample-events.jsonl"],
    },
]


def run_check(check: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    started = time.monotonic()
    completed = subprocess.run(
        check["cmd"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    duration_ms = int((time.monotonic() - started) * 1000)
    return {
        "id": check["id"],
        "description": check["description"],
        "cmd": check["cmd"],
        "status": "pass" if completed.returncode == 0 else "fail",
        "returncode": completed.returncode,
        "duration_ms": duration_ms,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def run_preflight(root: Path = ROOT, stop_on_failure: bool = False) -> dict[str, Any]:
    started = time.monotonic()
    results: list[dict[str, Any]] = []
    for check in CHECKS:
        result = run_check(check, root)
        results.append(result)
        if stop_on_failure and result["status"] == "fail":
            break

    failed = sum(1 for result in results if result["status"] == "fail")
    passed = len(results) - failed
    status = "pass" if failed == 0 and len(results) == len(CHECKS) else "fail"
    return {
        "status": status,
        "passed": passed,
        "failed": failed,
        "total": len(results),
        "defined_checks": len(CHECKS),
        "duration_ms": int((time.monotonic() - started) * 1000),
        "checks": results,
    }


def write_report(report_path: Path, result: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def print_text_report(result: dict[str, Any]) -> None:
    print(f"Local preflight: {result['status'].upper()} ({result['passed']}/{result['total']} passed)")
    for check in result["checks"]:
        print(f"- {check['id']}: {check['status'].upper()} ({check['duration_ms']} ms)")
        if check["status"] == "fail":
            stderr = check["stderr"].strip()
            stdout = check["stdout"].strip()
            if stderr:
                print(f"  stderr: {stderr}")
            if stdout:
                print(f"  stdout: {stdout}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    parser.add_argument(
        "--report",
        type=Path,
        nargs="?",
        const=DEFAULT_REPORT,
        help="Write a JSON report. Defaults to reports/local-checks-latest.json when no path is given.",
    )
    parser.add_argument("--stop-on-failure", action="store_true")
    args = parser.parse_args(argv)

    result = run_preflight(args.root, stop_on_failure=args.stop_on_failure)
    if args.report:
        write_report(args.report, result)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_text_report(result)
        if args.report:
            print(f"Report: {args.report}")

    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
