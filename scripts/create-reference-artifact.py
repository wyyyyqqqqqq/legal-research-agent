#!/usr/bin/env python3
"""Create and catalog a draft reference artifact or specialist pack."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = Path("references/reference-catalog.json")
CATALOG_CHECKER = ROOT / "scripts" / "check-reference-catalog.py"
CATALOG_VERSION = "1.0"
ALLOWED_KINDS = {"reference", "pack"}


def load_catalog_checker():
    spec = importlib.util.spec_from_file_location("check_reference_catalog", CATALOG_CHECKER)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {CATALOG_CHECKER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def kebab(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", normalized)


def title_case_from_id(artifact_id: str) -> str:
    return " ".join(part.capitalize() for part in artifact_id.split("-"))


def load_catalog(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": CATALOG_VERSION, "artifacts": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("catalog must be a JSON object")
    if data.get("version") != CATALOG_VERSION:
        raise ValueError(f"catalog version must be {CATALOG_VERSION!r}")
    artifacts = data.get("artifacts")
    if not isinstance(artifacts, list):
        raise ValueError("catalog artifacts must be a list")
    return data


def write_catalog(path: Path, catalog: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def owner_skill_exists(root: Path, owner_skill: str) -> bool:
    return (root / "skills" / f"{owner_skill}.md").exists() or (
        root / "skills" / "specialists" / f"{owner_skill}.md"
    ).exists()


def render_artifact(kind: str, title: str, owner_skill: str | None) -> tuple[str, list[str]]:
    if kind == "pack":
        heading = f"# {title} Reference Pack"
        owner_line = (
            f"Detailed drafting and quality-control framework for `{owner_skill}`."
            if owner_skill
            else "Detailed drafting and quality-control framework."
        )
        headings = [
            heading,
            "## Quick Start",
            "## Intake",
            "## Source Minimums",
            "## Output Quality Checklist",
            "## Pitfalls",
        ]
        text = f"""{heading}

{owner_line}

This pack is procedural. It describes what to verify and how to structure the
output; it is not cached legal authority.

## Quick Start

- Define the task scope and audience.
- Collect controlling source material before drafting.
- Use the checklist below before finalizing.

## Intake

| Item | Required | Notes |
|---|---:|---|
| Jurisdiction or source scope | Yes | |
| User objective | Yes | |
| Output shape | If specified | |

## Source Minimums

- Identify primary or official sources before making legal propositions.
- Record source gaps and currentness limitations.
- Do not rely on this pack as legal authority.

## Output Quality Checklist

- [ ] Scope and audience are explicit.
- [ ] Material propositions trace to source IDs.
- [ ] Currentness and effective dates are handled where relevant.
- [ ] Limitations are visible.

## Pitfalls

- Treating procedural guidance as current law.
- Omitting source gaps.
- Expanding beyond the requested deliverable.
"""
        return text, headings

    heading = f"# {title}"
    headings = [
        heading,
        "## Use When",
        "## Required Structure",
        "## Validation Rules",
        "## Quality Checklist",
    ]
    text = f"""{heading}

Reusable reference material for the legal research workflow.

## Use When

- Use this reference when the matching workflow needs a shared schema,
  template, or quality-control rule.

## Required Structure

- Define the input conditions.
- Define the output or validation shape.
- Define source, citation, or confidence handling where relevant.

## Validation Rules

- Keep headings stable.
- Keep the reference procedural unless it is explicitly a schema.
- Do not cache mutable legal authority.

## Quality Checklist

- [ ] Scope is clear.
- [ ] Required fields or sections are explicit.
- [ ] The reference can be validated deterministically.
"""
    return text, headings


def create_reference_artifact(
    *,
    root: Path = ROOT,
    kind: str,
    artifact_id: str,
    title: str | None = None,
    owner_skill: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    normalized_kind = kind.strip().lower()
    if normalized_kind not in ALLOWED_KINDS:
        raise ValueError(f"unsupported kind {kind!r}")

    normalized_id = kebab(artifact_id)
    if not normalized_id:
        raise ValueError("id must contain at least one alphanumeric character")

    title = (title or title_case_from_id(normalized_id)).strip()
    if not title:
        raise ValueError("title must be non-empty")

    if owner_skill:
        owner_skill = owner_skill.strip()
        if not owner_skill_exists(root, owner_skill):
            raise ValueError(f"owner skill {owner_skill!r} not found")

    relative_path = (
        Path("references") / "packs" / f"{normalized_id}.md"
        if normalized_kind == "pack"
        else Path("references") / f"{normalized_id}.md"
    )
    output_path = root / relative_path
    if output_path.exists():
        raise FileExistsError(f"{relative_path} already exists")

    catalog_path = root / CATALOG_PATH
    catalog = load_catalog(catalog_path)
    existing_ids = {
        str(entry.get("id", ""))
        for entry in catalog["artifacts"]
        if isinstance(entry, dict)
    }
    existing_paths = {
        str(entry.get("path", ""))
        for entry in catalog["artifacts"]
        if isinstance(entry, dict)
    }
    if normalized_id in existing_ids:
        raise ValueError(f"catalog already contains artifact id {normalized_id!r}")
    if str(relative_path) in existing_paths:
        raise ValueError(f"catalog already contains path {str(relative_path)!r}")

    text, headings = render_artifact(normalized_kind, title, owner_skill)
    entry: dict[str, Any] = {
        "id": normalized_id,
        "kind": normalized_kind,
        "path": str(relative_path),
        "status": "draft",
        "min_bytes": 200,
        "required_headings": headings,
    }
    if owner_skill:
        entry["owner_skill"] = owner_skill

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text, encoding="utf-8")
    catalog["artifacts"].append(entry)
    write_catalog(catalog_path, catalog)

    errors = load_catalog_checker().check(root)
    if errors:
        raise RuntimeError("created artifact but catalog validation failed: " + "; ".join(errors))

    return output_path, entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--kind", choices=sorted(ALLOWED_KINDS), required=True)
    parser.add_argument("--id", required=True)
    parser.add_argument("--title")
    parser.add_argument("--owner-skill")
    args = parser.parse_args(argv)

    try:
        path, entry = create_reference_artifact(
            root=args.root,
            kind=args.kind,
            artifact_id=args.id,
            title=args.title,
            owner_skill=args.owner_skill,
        )
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"Created: {path}")
    print(f"Cataloged: {entry['id']} ({entry['status']})")
    print("Next: fill the draft, wire any skill load rule, then run:")
    print("  python3 scripts/check-reference-catalog.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
