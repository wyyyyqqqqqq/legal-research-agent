#!/usr/bin/env python3
"""Validate internal Markdown reference paths in active instructions and docs."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SCAN_PATHS = [
    "CLAUDE.md",
    "README.md",
    "README.ko.md",
    "docs",
    "skills",
    "knowledge",
    "references",
    "templates",
    "scripts",
]

SCAN_SUFFIXES = {".md", ".py"}

PATH_RE = re.compile(
    r"(?<![\w./-])("
    r"(?:references|knowledge|templates)/(?:[\w.-]+/)*[\w.-]+\.md"
    r"|\.claude/(?:[\w.-]+/)*[\w.-]+\.md"
    r")(?![\w.-])"
)
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
VALIDATED_PREFIXES = ("references/", "knowledge/", "templates/", ".claude/")

INLINE_IGNORE_MARKERS = {
    "legacy path",
    "historical reference",
    "archive-only",
    "intentionally missing",
    "unresolved example",
}


def iter_scan_files(root: Path, include_archive: bool = False) -> list[Path]:
    files: list[Path] = []
    for entry in SCAN_PATHS:
        path = root / entry
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix in SCAN_SUFFIXES:
                files.append(path)
            continue
        for child in path.rglob("*"):
            if not child.is_file() or child.suffix not in SCAN_SUFFIXES:
                continue
            relative = child.relative_to(root)
            if not include_archive and relative.parts[:2] == ("docs", "archive"):
                continue
            files.append(child)
    return sorted(set(files))


def line_is_ignored(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in INLINE_IGNORE_MARKERS)


def clean_markdown_target(raw_target: str) -> str | None:
    target = raw_target.strip()
    if not target:
        return None
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    elif " " in target:
        target = target.split()[0].strip()
    if not target or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None
    if target.startswith("#"):
        return None
    target = target.split("#", 1)[0].split("?", 1)[0].strip()
    if target.startswith("/"):
        target = target.lstrip("/")
    if target.startswith("./"):
        target = target[2:]
    return target or None


def target_to_repo_relative(root: Path, source_path: Path, target: str) -> str | None:
    if target.startswith(VALIDATED_PREFIXES):
        return target
    resolved = (source_path.parent / target).resolve()
    try:
        relative = resolved.relative_to(root.resolve())
    except ValueError:
        return None
    relative_text = str(relative)
    if relative_text.startswith(VALIDATED_PREFIXES):
        return relative_text
    return None


def extract_reference_targets(root: Path, source_path: Path, line: str) -> set[str]:
    targets = {match.group(1) for match in PATH_RE.finditer(line)}
    for match in MARKDOWN_LINK_RE.finditer(line):
        cleaned = clean_markdown_target(match.group(1))
        if not cleaned:
            continue
        relative = target_to_repo_relative(root, source_path, cleaned)
        if relative:
            targets.add(relative)
    return targets


def check(root: Path = ROOT, include_archive: bool = False) -> list[str]:
    errors: list[str] = []
    for path in iter_scan_files(root, include_archive=include_archive):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{path.relative_to(root)}: cannot read as UTF-8")
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            if line_is_ignored(line):
                continue
            for target in sorted(extract_reference_targets(root, path, line)):
                if not (root / target).exists():
                    errors.append(
                        f"{path.relative_to(root)}:{lineno}: missing internal reference {target!r}"
                    )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--include-archive",
        action="store_true",
        help="Also scan docs/archive/ historical plans.",
    )
    args = parser.parse_args(argv)

    errors = check(args.root, include_archive=args.include_archive)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: internal reference links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
