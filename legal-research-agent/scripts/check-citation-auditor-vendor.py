#!/usr/bin/env python3
"""Validate the vendored citation-auditor integration."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_VERSION = "1.4.0"
REQUIRED_PATHS = [
    ".claude/commands/audit.md",
    ".claude/skills/README.md",
    ".claude/skills/citation-auditor/SKILL.md",
    ".claude/skills/citation-auditor/VENDOR.md",
    ".claude/skills/verifiers/eu-law/SKILL.md",
    ".claude/skills/verifiers/general-web/SKILL.md",
    ".claude/skills/verifiers/korean-law/SKILL.md",
    ".claude/skills/verifiers/scholarly/SKILL.md",
    ".claude/skills/verifiers/uk-law/SKILL.md",
    ".claude/skills/verifiers/us-law/SKILL.md",
    ".claude/skills/verifiers/wikipedia/SKILL.md",
    "citation_auditor/__init__.py",
    "citation_auditor/__main__.py",
    "citation_auditor/aggregation.py",
    "citation_auditor/chunking.py",
    "citation_auditor/docx.py",
    "citation_auditor/finalize.py",
    "citation_auditor/korean_law.py",
    "citation_auditor/models.py",
    "citation_auditor/prepare.py",
    "citation_auditor/render.py",
    "citation_auditor/report.py",
    "citation_auditor/settings.py",
]
REQUIRED_HELP_TERMS = {
    "chunk",
    "aggregate",
    "prepare",
    "finalize",
    "extract-docx",
    "korean_law",
}
REQUIRED_DEPENDENCIES = {
    "marko",
    "pydantic",
}


def vendor_version(vendor_path: Path) -> str | None:
    text = vendor_path.read_text(encoding="utf-8")
    match = re.search(r"^- Version:\s+\*\*v?([^*]+)\*\*", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def check_vendor(root: Path = ROOT, expected_version: str = EXPECTED_VERSION, run_cli: bool = True) -> list[str]:
    errors: list[str] = []

    for relative_path in REQUIRED_PATHS:
        path = root / relative_path
        if not path.exists():
            errors.append(f"missing vendored citation-auditor path: {relative_path}")
        elif path.is_symlink():
            errors.append(f"vendored citation-auditor path must not be a symlink: {relative_path}")
        elif path.is_file() and not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty vendored citation-auditor file: {relative_path}")

    vendor_path = root / ".claude/skills/citation-auditor/VENDOR.md"
    if vendor_path.exists():
        actual_version = vendor_version(vendor_path)
        if actual_version != expected_version:
            errors.append(
                "citation-auditor vendor version mismatch: "
                f"expected {expected_version!r}, got {actual_version!r}"
            )

    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.exists():
        errors.append("missing pyproject.toml for citation-auditor dependencies")
    else:
        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
        dependencies = pyproject.get("project", {}).get("dependencies", [])
        declared = {str(dependency).split(">", 1)[0].split("=", 1)[0].split("<", 1)[0].strip() for dependency in dependencies}
        missing_dependencies = sorted(REQUIRED_DEPENDENCIES - declared)
        if missing_dependencies:
            errors.append(f"pyproject.toml missing citation-auditor dependencies: {missing_dependencies}")

    if run_cli:
        completed = subprocess.run(
            ["python3", "-m", "citation_auditor", "--help"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            errors.append(
                "citation-auditor CLI help failed: "
                f"returncode={completed.returncode}, stderr={completed.stderr.strip()!r}"
            )
        else:
            help_text = completed.stdout
            missing_terms = sorted(term for term in REQUIRED_HELP_TERMS if term not in help_text)
            if missing_terms:
                errors.append(f"citation-auditor CLI help missing commands: {missing_terms}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--expected-version", default=EXPECTED_VERSION)
    parser.add_argument("--no-cli", action="store_true", help="Skip python -m citation_auditor --help smoke test.")
    args = parser.parse_args(argv)

    errors = check_vendor(args.root, args.expected_version, run_cli=not args.no_cli)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: citation-auditor vendor integration valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
