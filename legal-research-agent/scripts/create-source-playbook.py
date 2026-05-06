#!/usr/bin/env python3
"""Create and register a draft general-law source playbook."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = Path("knowledge/general/source-playbook-index.json")
PLAYBOOK_DIR = Path("knowledge/general/playbooks")
TEMPLATE_PATH = Path("templates/source-playbook.example.md")
REGISTRY_VERSION = "1.0"

ALLOWED_JURISDICTIONS = {"KR", "US", "EU", "JP", "UK", "MULTI"}
ALLOWED_DOMAINS = {
    "administrative",
    "civil_liability",
    "consumer_ecommerce",
    "contracts_commercial",
    "corporate",
    "employment",
    "general",
    "platform_service",
    "tax",
}
ALLOWED_STATUSES = {"draft", "active", "deprecated"}


def normalize_jurisdiction(value: str) -> str:
    return value.strip().upper()


def normalize_domain(value: str) -> str:
    return value.strip().lower().replace("-", "_")


def kebab(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return re.sub(r"-+", "-", normalized)


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": REGISTRY_VERSION, "playbooks": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("registry must be a JSON object")
    if data.get("version") != REGISTRY_VERSION:
        raise ValueError(f"registry version must be {REGISTRY_VERSION!r}")
    playbooks = data.get("playbooks")
    if not isinstance(playbooks, list):
        raise ValueError("registry playbooks must be a list")
    return data


def write_registry(path: Path, registry: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def render_template(
    template: str,
    *,
    title: str,
    playbook_id: str,
    jurisdiction: str,
    domain: str,
    status: str,
    owner: str,
    last_reviewed: str,
) -> str:
    replacements = {
        "{Title}": title,
        "{id}": playbook_id,
        "{jurisdiction}": jurisdiction,
        "{domain}": domain,
        "{status}": status,
        "{owner}": owner,
        "{last_reviewed}": last_reviewed,
    }
    rendered = template
    for placeholder, value in replacements.items():
        rendered = rendered.replace(placeholder, value)
    return rendered


def create_playbook(
    *,
    root: Path = ROOT,
    jurisdiction: str,
    domain: str,
    title: str,
    status: str = "draft",
    owner: str = "unassigned",
    last_reviewed: str | None = None,
) -> tuple[Path, dict[str, str]]:
    normalized_jurisdiction = normalize_jurisdiction(jurisdiction)
    normalized_domain = normalize_domain(domain)
    normalized_status = status.strip().lower()
    owner = owner.strip() or "unassigned"
    last_reviewed = last_reviewed or date.today().isoformat()

    if normalized_jurisdiction not in ALLOWED_JURISDICTIONS:
        raise ValueError(f"unsupported jurisdiction {normalized_jurisdiction!r}")
    if normalized_domain not in ALLOWED_DOMAINS:
        raise ValueError(f"unsupported domain {normalized_domain!r}")
    if normalized_status not in ALLOWED_STATUSES:
        raise ValueError(f"unsupported status {normalized_status!r}")
    if not title.strip():
        raise ValueError("title must be non-empty")

    playbook_id = f"{normalized_jurisdiction.lower()}-{kebab(normalized_domain)}"
    relative_path = PLAYBOOK_DIR / f"{playbook_id}.md"
    output_path = root / relative_path
    registry_path = root / REGISTRY_PATH
    template_path = root / TEMPLATE_PATH

    if output_path.exists():
        raise FileExistsError(f"{relative_path} already exists")
    if not template_path.exists():
        raise FileNotFoundError(f"{TEMPLATE_PATH} is missing")

    registry = load_registry(registry_path)
    existing_ids = {
        str(entry.get("id", ""))
        for entry in registry.get("playbooks", [])
        if isinstance(entry, dict)
    }
    if playbook_id in existing_ids:
        raise ValueError(f"registry already contains playbook id {playbook_id!r}")

    entry = {
        "id": playbook_id,
        "jurisdiction": normalized_jurisdiction,
        "domain": normalized_domain,
        "path": str(relative_path),
        "status": normalized_status,
    }

    template = template_path.read_text(encoding="utf-8")
    output_text = render_template(
        template,
        title=title.strip(),
        playbook_id=playbook_id,
        jurisdiction=normalized_jurisdiction,
        domain=normalized_domain,
        status=normalized_status,
        owner=owner,
        last_reviewed=last_reviewed,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output_text, encoding="utf-8")
    registry["playbooks"].append(entry)
    write_registry(registry_path, registry)

    return output_path, entry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--jurisdiction", required=True)
    parser.add_argument("--domain", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--status", choices=sorted(ALLOWED_STATUSES), default="draft")
    parser.add_argument("--owner", default="unassigned")
    parser.add_argument("--last-reviewed")
    args = parser.parse_args(argv)

    try:
        path, entry = create_playbook(
            root=args.root,
            jurisdiction=args.jurisdiction,
            domain=args.domain,
            title=args.title,
            status=args.status,
            owner=args.owner,
            last_reviewed=args.last_reviewed,
        )
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    print(f"Created: {path}")
    print(f"Registered: {entry['id']}")
    print("Fill the TODO sections, then run: python3 scripts/check-source-playbooks.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
