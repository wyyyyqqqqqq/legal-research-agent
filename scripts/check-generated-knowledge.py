#!/usr/bin/env python3
"""Validate generated knowledge directories against the construction recipe.

Skips when no generated directories exist. Validates:
- All four required Markdown files present
- review-status.json present and valid
- Banner block on every Markdown file (matching review_status)
- YAML frontmatter with required fields
- Recipe version compatibility
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MARKDOWN_FILES = [
    "issue-taxonomy.md",
    "regulatory-map.md",
    "source-map.md",
    "library-index.md",
]

REQUIRED_REVIEW_STATUS_FIELDS = {
    "industry",
    "area_of_law",
    "jurisdiction",
    "review_status",
    "source_audit_status",
    "created_at",
    "recipe_version",
}

ALLOWED_REVIEW_STATUSES = {"draft", "verified"}
ALLOWED_AUDIT_STATUSES = {
    "not_required",
    "not_run_session_unavailable",
    "deterministic_smoke",
    "live_passed",
    "live_failed",
}
RECIPE_SUPPORTED_VERSIONS = {"1.0"}

DRAFT_BANNER = re.compile(
    r">\s*\*\*\[GENERATED\s+—\s+REQUIRES HUMAN REVIEW\]\*\*"
)
VERIFIED_BANNER = re.compile(r">\s*\*\*\[VERIFIED\]\*\*")
FRONTMATTER_DELIMITER = "---"
REQUIRED_FRONTMATTER_FIELDS = {
    "industry",
    "area_of_law",
    "jurisdiction",
    "recipe_version",
    "generated_at",
    "verification_status",
}

# Hand-curated and infrastructure dirs under knowledge/ that are NOT
# generated. They follow their own conventions and the validator
# must skip them.
HAND_CURATED_DIRS = {
    "game-regulation",
    "general",
    "legal-writing",
    "onboarding",
    "output-modes",
}


def find_generated_dirs(root: Path) -> list[Path]:
    """Find any knowledge/<industry>-<area>/ directory.

    A generated dir is identified by:
      - sitting directly under knowledge/
      - containing a hyphen in its name
      - NOT being one of the known hand-curated infrastructure dirs
    """
    knowledge = root / "knowledge"
    if not knowledge.is_dir():
        return []
    candidates: list[Path] = []
    for child in sorted(knowledge.iterdir()):
        if not child.is_dir():
            continue
        if child.name in HAND_CURATED_DIRS:
            continue
        if "-" in child.name:
            candidates.append(child)
    return candidates


def parse_frontmatter(path: Path) -> tuple[str, dict[str, str]]:
    """Return (banner_line, frontmatter_dict).

    The banner_line is the first non-empty line of the file. Frontmatter
    is parsed with a tiny inline parser keyed on the leading and
    trailing `---` delimiters.
    """
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    banner_line = ""
    for line in lines:
        if line.strip():
            banner_line = line
            break
    frontmatter: dict[str, str] = {}
    in_fm = False
    for line in lines:
        stripped = line.strip()
        if stripped == FRONTMATTER_DELIMITER:
            if in_fm:
                break
            in_fm = True
            continue
        if in_fm and ":" in line:
            key, _, value = line.partition(":")
            frontmatter[key.strip()] = value.strip()
    return banner_line, frontmatter


def validate_dir(path: Path) -> list[str]:
    errors: list[str] = []

    for required in REQUIRED_MARKDOWN_FILES:
        if not (path / required).exists():
            errors.append(f"{path}: missing required file {required}")

    review_path = path / "review-status.json"
    if not review_path.exists():
        errors.append(f"{path}: missing review-status.json")
        return errors

    try:
        review = json.loads(review_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{review_path}: invalid JSON ({exc})")
        return errors

    missing_fields = REQUIRED_REVIEW_STATUS_FIELDS - set(review)
    if missing_fields:
        errors.append(
            f"{review_path}: missing fields {sorted(missing_fields)}"
        )

    if review.get("review_status") not in ALLOWED_REVIEW_STATUSES:
        errors.append(
            f"{review_path}: review_status must be one of "
            f"{sorted(ALLOWED_REVIEW_STATUSES)} "
            f"(got {review.get('review_status')!r})"
        )

    if review.get("source_audit_status") not in ALLOWED_AUDIT_STATUSES:
        errors.append(
            f"{review_path}: source_audit_status must be one of "
            f"{sorted(ALLOWED_AUDIT_STATUSES)} "
            f"(got {review.get('source_audit_status')!r})"
        )

    if review.get("recipe_version") not in RECIPE_SUPPORTED_VERSIONS:
        errors.append(
            f"{review_path}: recipe_version must be one of "
            f"{sorted(RECIPE_SUPPORTED_VERSIONS)} "
            f"(got {review.get('recipe_version')!r})"
        )

    expected_banner = (
        DRAFT_BANNER
        if review.get("review_status") == "draft"
        else VERIFIED_BANNER
    )

    for md_name in REQUIRED_MARKDOWN_FILES:
        md_path = path / md_name
        if not md_path.exists():
            continue
        banner_line, frontmatter = parse_frontmatter(md_path)
        if not expected_banner.search(banner_line):
            errors.append(
                f"{md_path}: missing or wrong banner for "
                f"review_status={review.get('review_status')!r} "
                f"(got {banner_line!r})"
            )
        missing_fm = REQUIRED_FRONTMATTER_FIELDS - set(frontmatter)
        if missing_fm:
            errors.append(
                f"{md_path}: frontmatter missing fields {sorted(missing_fm)}"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument(
        "--dir",
        action="append",
        type=Path,
        default=[],
        help=(
            "Validate the named directory instead of auto-discovering. "
            "May be repeated."
        ),
    )
    args = parser.parse_args(argv)

    dirs = list(args.dir) if args.dir else find_generated_dirs(args.root)
    if not dirs:
        print("SKIP: no generated knowledge directories present")
        return 0

    all_errors: list[str] = []
    for d in dirs:
        if not d.exists():
            all_errors.append(f"{d}: directory does not exist")
            continue
        all_errors.extend(validate_dir(d))

    if all_errors:
        for line in all_errors:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1

    print(f"OK: {len(dirs)} generated knowledge directory/directories valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
