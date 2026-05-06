#!/usr/bin/env python3
"""Aggregate token usage from Claude Code events.jsonl files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


TOKEN_KEYS = {
    "input": "input_tokens",
    "output": "output_tokens",
    "cache_read": "cache_read_input_tokens",
    "cache_create": "cache_creation_input_tokens",
}


def iter_events(path: Path) -> tuple[list[dict[str, Any]], int]:
    events: list[dict[str, Any]] = []
    skipped = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            skipped += 1
            continue
        if isinstance(event, dict):
            events.append(event)
        else:
            skipped += 1
    return events, skipped


def aggregate_tokens(events: list[dict[str, Any]]) -> dict[str, int]:
    totals = {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0}
    for event in events:
        usage = event.get("usage")
        if not isinstance(usage, dict):
            continue
        for total_key, usage_key in TOKEN_KEYS.items():
            value = usage.get(usage_key, 0)
            if isinstance(value, int):
                totals[total_key] += value
    totals["total_billed_like"] = totals["input"] + totals["output"] + totals["cache_create"]
    return totals


def summarize_file(path: Path) -> dict[str, Any]:
    events, skipped = iter_events(path)
    usage_events = [event for event in events if isinstance(event.get("usage"), dict)]
    totals = aggregate_tokens(events)
    return {
        "path": str(path),
        "events": len(events),
        "usage_events": len(usage_events),
        "skipped_lines": skipped,
        "tokens": totals,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events_jsonl", nargs="+", type=Path)
    args = parser.parse_args(argv)

    summaries = []
    exit_code = 0
    for path in args.events_jsonl:
        if not path.exists():
            print(f"WARN: missing events file: {path}", file=sys.stderr)
            exit_code = 1
            continue
        summaries.append(summarize_file(path))

    grand_total = {"input": 0, "output": 0, "cache_read": 0, "cache_create": 0, "total_billed_like": 0}
    for summary in summaries:
        for key in grand_total:
            grand_total[key] += summary["tokens"][key]

    print(json.dumps({"files": summaries, "grand_total": grand_total}, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
