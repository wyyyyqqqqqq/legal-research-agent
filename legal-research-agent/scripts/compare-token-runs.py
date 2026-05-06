#!/usr/bin/env python3
"""Compare legacy and merged token usage by route pattern."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MEASURE_TOKENS_PATH = ROOT / "scripts" / "measure-tokens.py"
VALID_ROUTE_PATTERNS = {
    "general-only",
    "game-only",
    "game-plus-general",
    "game-plus-data-protection",
    "multi-jurisdiction-game",
    "routing-edge-case",
    "fallback",
}
TOKEN_TOTAL_KEY = "total_billed_like"
PROXY_KEYS = ("agent_calls", "result_bytes", "wall_clock_ms")


def load_measure_tokens():
    spec = importlib.util.spec_from_file_location("measure_tokens", MEASURE_TOKENS_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load measure-tokens.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MEASURE_TOKENS = load_measure_tokens()


class TokenComparisonError(Exception):
    """Raised when a token comparison manifest is not usable."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TokenComparisonError(f"{path}: invalid JSON: {exc}") from exc


def resolve_manifest_path(manifest_path: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (manifest_path.parent / path).resolve()


def empty_token_totals() -> dict[str, int]:
    return {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0, TOKEN_TOTAL_KEY: 0}


def summarize_events(manifest_path: Path, event_paths: list[Any]) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    tokens = empty_token_totals()
    for raw_path in event_paths:
        if not isinstance(raw_path, str) or not raw_path.strip():
            raise TokenComparisonError("events entries must be non-empty strings")
        path = resolve_manifest_path(manifest_path, raw_path)
        if not path.exists():
            raise TokenComparisonError(f"events file does not exist: {path}")
        summary = MEASURE_TOKENS.summarize_file(path)
        files.append(summary)
        for key in tokens:
            tokens[key] += int(summary["tokens"][key])
    return {
        "measurement_type": "actual_events",
        "events_files": files,
        "tokens": tokens,
    }


def normalize_proxy_metrics(value: Any) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise TokenComparisonError("proxy_metrics must be an object")
    metrics: dict[str, int] = {}
    for key in PROXY_KEYS:
        if key not in value:
            continue
        raw_metric = value[key]
        if not isinstance(raw_metric, int) or raw_metric < 0:
            raise TokenComparisonError(f"proxy_metrics.{key} must be a non-negative integer")
        metrics[key] = raw_metric
    return metrics


def quality_report_summary(manifest_path: Path, item: dict[str, Any], quality_status: str) -> dict[str, Any] | None:
    report_ref = item.get("quality_report")
    if report_ref is None:
        return None
    if not isinstance(report_ref, str) or not report_ref.strip():
        raise TokenComparisonError("quality_report must be a non-empty string when provided")

    report_path = resolve_manifest_path(manifest_path, report_ref)
    if not report_path.exists():
        raise TokenComparisonError(f"quality_report does not exist: {report_path}")
    report = load_json(report_path)
    if not isinstance(report, dict):
        raise TokenComparisonError(f"{report_path}: quality_report must be a JSON object")

    report_status = str(report.get("status", "")).lower()
    if report_status not in {"pass", "fail", "unknown"}:
        raise TokenComparisonError(f"{report_path}: quality_report.status must be pass, fail, or unknown")

    case_id = item.get("case_id")
    report_case_id = report.get("case_id")
    return {
        "path": str(report_path),
        "status": report_status,
        "case_id": report_case_id,
        "matches_quality_status": report_status == quality_status,
        "matches_case_id": not case_id or not report_case_id or report_case_id == case_id,
    }


def summarize_run(manifest_path: Path, run: Any, label: str) -> dict[str, Any]:
    if not isinstance(run, dict):
        raise TokenComparisonError(f"{label}: run must be an object")

    events = run.get("events", [])
    if events:
        if not isinstance(events, list):
            raise TokenComparisonError(f"{label}: events must be a list")
        summary = summarize_events(manifest_path, events)
    else:
        proxy_metrics = normalize_proxy_metrics(run.get("proxy_metrics"))
        if not proxy_metrics:
            raise TokenComparisonError(f"{label}: provide events or proxy_metrics")
        summary = {
            "measurement_type": "proxy",
            "proxy_metrics": proxy_metrics,
            "tokens": empty_token_totals(),
        }

    if "agent_calls" in run:
        agent_calls = run["agent_calls"]
        if not isinstance(agent_calls, int) or agent_calls < 0:
            raise TokenComparisonError(f"{label}: agent_calls must be a non-negative integer")
        summary["agent_calls"] = agent_calls

    summary["label"] = str(run.get("label", label))
    return summary


def token_delta(legacy: dict[str, Any], merged: dict[str, Any]) -> int | None:
    if legacy["measurement_type"] != "actual_events" or merged["measurement_type"] != "actual_events":
        return None
    return int(merged["tokens"][TOKEN_TOTAL_KEY]) - int(legacy["tokens"][TOKEN_TOTAL_KEY])


def percent_delta(delta: int | None, legacy_total: int) -> float | None:
    if delta is None or legacy_total == 0:
        return None
    return round((delta / legacy_total) * 100, 2)


def compare_pattern(manifest_path: Path, item: Any, index: int) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise TokenComparisonError(f"patterns[{index}]: expected object")

    route_pattern = item.get("route_pattern")
    if route_pattern not in VALID_ROUTE_PATTERNS:
        raise TokenComparisonError(
            f"patterns[{index}].route_pattern must be one of {sorted(VALID_ROUTE_PATTERNS)}"
        )

    quality_status = str(item.get("quality_status", "")).lower()
    if quality_status not in {"pass", "fail", "unknown"}:
        raise TokenComparisonError(
            f"patterns[{index}].quality_status must be pass, fail, or unknown"
        )

    legacy = summarize_run(manifest_path, item.get("legacy"), f"patterns[{index}].legacy")
    merged = summarize_run(manifest_path, item.get("merged"), f"patterns[{index}].merged")
    delta = token_delta(legacy, merged)
    legacy_total = int(legacy["tokens"][TOKEN_TOTAL_KEY])
    quality_reason = str(item.get("quality_reason", "")).strip()
    quality_report = quality_report_summary(manifest_path, item, quality_status)

    errors: list[str] = []
    warnings: list[str] = []
    decision = "review"

    if quality_report:
        if not quality_report["matches_quality_status"]:
            errors.append(
                "quality_report: status mismatch "
                f"manifest={quality_status!r} report={quality_report['status']!r}"
            )
        if not quality_report["matches_case_id"]:
            errors.append(
                "quality_report: case_id mismatch "
                f"manifest={item.get('case_id')!r} report={quality_report['case_id']!r}"
            )

    if quality_status != "pass":
        errors.append(f"quality_status: expected 'pass', got {quality_status!r}")
        decision = "blocked_quality"
    elif delta is None:
        warnings.append("token_delta: proxy metrics only; actual events are needed before rollout decisions")
        decision = "proxy_only_review"
    elif delta < 0:
        decision = "token_savings"
    elif delta == 0:
        decision = "token_neutral"
    elif quality_reason:
        decision = "token_increase_with_quality_reason"
    else:
        errors.append("token_delta: merged run increased tokens without quality_reason")
        decision = "blocked_token_increase"

    return {
        "case_id": item.get("case_id"),
        "route_pattern": route_pattern,
        "quality_status": quality_status,
        "quality_reason": quality_reason or None,
        "quality_report": quality_report,
        "legacy": legacy,
        "merged": merged,
        "delta": {
            TOKEN_TOTAL_KEY: delta,
            "percent": percent_delta(delta, legacy_total),
        },
        "decision": decision,
        "status": "fail" if errors else "pass",
        "errors": errors,
        "warnings": warnings,
    }


def compare_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = load_json(manifest_path)
    if not isinstance(manifest, dict):
        raise TokenComparisonError("manifest must be a JSON object")
    patterns = manifest.get("patterns")
    if not isinstance(patterns, list) or not patterns:
        raise TokenComparisonError("manifest.patterns must be a non-empty list")

    comparisons = [
        compare_pattern(manifest_path, item, index)
        for index, item in enumerate(patterns)
    ]
    failed = sum(1 for comparison in comparisons if comparison["status"] == "fail")
    warnings = sum(len(comparison["warnings"]) for comparison in comparisons)
    return {
        "status": "fail" if failed else "pass",
        "manifest": str(manifest_path),
        "patterns": comparisons,
        "passed": len(comparisons) - failed,
        "failed": failed,
        "warnings": warnings,
    }


def print_text_report(result: dict[str, Any]) -> None:
    print(f"Token comparison: {result['status'].upper()} ({result['passed']}/{len(result['patterns'])} passed)")
    for pattern in result["patterns"]:
        delta = pattern["delta"][TOKEN_TOTAL_KEY]
        if delta is None:
            delta_text = "proxy-only"
        else:
            delta_text = f"{delta:+d}"
            if pattern["delta"]["percent"] is not None:
                delta_text += f" ({pattern['delta']['percent']:+.2f}%)"
        print(
            f"- {pattern['route_pattern']}: {pattern['decision']} "
            f"delta={delta_text} status={pattern['status']}"
        )
        for error in pattern["errors"]:
            print(f"  FAIL: {error}")
        for warning in pattern["warnings"]:
            print(f"  WARN: {warning}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    args = parser.parse_args(argv)

    try:
        result = compare_manifest(args.manifest)
    except TokenComparisonError as exc:
        if args.json:
            print(json.dumps({"status": "fail", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_text_report(result)

    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
