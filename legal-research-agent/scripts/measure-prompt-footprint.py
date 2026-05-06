#!/usr/bin/env python3
"""Measure the core prompt/instruction footprint for this agent repo."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORE_PATHS = ("CLAUDE.md", "skills", "knowledge", "templates")
VENDOR_PATHS = (".claude/commands", ".claude/skills")
MEASURED_SUFFIXES = {".md", ".json"}
SKIP_DIRS = {"__pycache__", ".git"}


def rough_token_count(text: str) -> int:
    """Return a stable local token proxy for prompt-footprint comparison."""
    if not text:
        return 0
    return math.ceil(len(text) / 4)


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))


def is_measured_file(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in MEASURED_SUFFIXES


def iter_files_under(path: Path) -> list[Path]:
    if is_measured_file(path):
        return [path]
    if not path.is_dir():
        return []

    files: list[Path] = []
    for candidate in path.rglob("*"):
        if any(part in SKIP_DIRS for part in candidate.parts):
            continue
        if is_measured_file(candidate):
            files.append(candidate)
    return files


def prompt_files(root: Path, include_vendor: bool = False) -> list[Path]:
    paths = list(CORE_PATHS)
    if include_vendor:
        paths.extend(VENDOR_PATHS)

    files: list[Path] = []
    seen: set[Path] = set()
    for relative in paths:
        for path in iter_files_under(root / relative):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def category_for(root: Path, path: Path) -> str:
    relative = path.relative_to(root)
    first = relative.parts[0]
    if first == "CLAUDE.md":
        return "agent_prompt"
    if first == ".claude":
        return "vendor_claude"
    return first


def empty_totals() -> dict[str, int]:
    return {"files": 0, "bytes": 0, "chars": 0, "words": 0, "rough_tokens": 0}


def add_totals(target: dict[str, int], item: dict[str, int]) -> None:
    for key in target:
        target[key] += item[key]


def summarize_file(root: Path, path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    encoded = text.encode("utf-8")
    return {
        "path": path.relative_to(root).as_posix(),
        "category": category_for(root, path),
        "bytes": len(encoded),
        "chars": len(text),
        "words": word_count(text),
        "rough_tokens": rough_token_count(text),
    }


def summarize_root(root: Path, include_vendor: bool = False) -> dict[str, Any]:
    if not root.exists():
        raise FileNotFoundError(f"root does not exist: {root}")

    file_summaries = [summarize_file(root, path) for path in prompt_files(root, include_vendor)]
    totals = empty_totals()
    by_category: dict[str, dict[str, int]] = {}

    for summary in file_summaries:
        item_totals = {
            "files": 1,
            "bytes": int(summary["bytes"]),
            "chars": int(summary["chars"]),
            "words": int(summary["words"]),
            "rough_tokens": int(summary["rough_tokens"]),
        }
        add_totals(totals, item_totals)
        category = str(summary["category"])
        by_category.setdefault(category, empty_totals())
        add_totals(by_category[category], item_totals)

    return {
        "root": str(root),
        "profile": "core_plus_vendor" if include_vendor else "core",
        "token_proxy": "ceil(characters/4)",
        "measured_suffixes": sorted(MEASURED_SUFFIXES),
        "totals": totals,
        "by_category": dict(sorted(by_category.items())),
        "files": file_summaries,
    }


def print_text_summary(summary: dict[str, Any]) -> None:
    totals = summary["totals"]
    print(
        "Prompt footprint: "
        f"{totals['rough_tokens']} rough tokens across {totals['files']} files "
        f"({totals['chars']} chars)"
    )
    for category, values in summary["by_category"].items():
        print(
            f"- {category}: {values['rough_tokens']} rough tokens, "
            f"{values['files']} files"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--include-vendor", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only.")
    parser.add_argument("--write-report", type=Path, help="Write the measurement JSON to this path.")
    parser.add_argument(
        "--max-rough-tokens",
        type=int,
        help="Fail when the measured rough token total exceeds this budget.",
    )
    args = parser.parse_args(argv)

    try:
        summary = summarize_root(args.root, include_vendor=args.include_vendor)
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.write_report:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    total = int(summary["totals"]["rough_tokens"])
    over_budget = args.max_rough_tokens is not None and total > args.max_rough_tokens

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_text_summary(summary)

    if over_budget:
        print(
            f"FAIL: prompt footprint {total} exceeds rough-token budget "
            f"{args.max_rough_tokens}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
