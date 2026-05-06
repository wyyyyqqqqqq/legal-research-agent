#!/usr/bin/env python3
"""Unit tests for source playbook authoring and validation."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = ROOT / "scripts" / "check-source-playbooks.py"
CREATOR_PATH = ROOT / "scripts" / "create-source-playbook.py"
TEMPLATE_PATH = ROOT / "templates" / "source-playbook.example.md"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load_module("check_source_playbooks", CHECKER_PATH)
CREATOR = load_module("create_source_playbook", CREATOR_PATH)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def prepare_temp_root(root: Path) -> None:
    (root / "knowledge/general/playbooks").mkdir(parents=True)
    (root / "templates").mkdir()
    (root / "templates/source-playbook.example.md").write_text(
        TEMPLATE_PATH.read_text(encoding="utf-8"),
        encoding="utf-8",
    )


def valid_playbook_text() -> str:
    return """# KR Platform Service

## Metadata

- id: kr-platform-service
- jurisdiction: KR
- domain: platform_service
- status: active
- owner: legal-research-agent
- last_reviewed: 2026-05-06

## Scope

Korean platform service questions where the service operator's basic statutory,
delegated-rule, regulator-guidance, and consumer/e-commerce source layers must
be checked before reaching a confidence rating.

## Required Source Layers

- Primary statute for the platform-service issue.
- Enforcement decree or rule where the statute delegates implementation detail.
- Regulator guidance, notices, FAQs, or enforcement positions where practical
  compliance turns on agency interpretation.

## Official Source Entry Points

- Official statute database.
- Competent ministry or regulator website.
- Official court or agency decision database when interpretation is controlling.

## Delegated Rule Checks

Check enforcement decrees, enforcement rules, notices, and published guidance
before treating a statutory rule as complete.

## Case Law Or Agency Decision Checks

Check cases or agency decisions when liability standards, remedies, or sanction
thresholds depend on interpretation rather than plain statutory text.

## Currentness Checks

Confirm the current official version, effective dates, pending amendments, and
whether guidance has been superseded before assigning high confidence.

## Common Pitfalls

- Treating an English summary as controlling law.
- Stopping at the statute when delegated rules provide operative detail.

## Fallback Behavior

If any required layer cannot be verified, lower confidence and record a
source-coverage or temporal-status gap.

## Example Source Plan

For a terms-change question, collect the governing statute, delegated rule,
agency guidance on notice, and any relevant enforcement examples before
drafting the short answer.
"""


class SourcePlaybooksTest(unittest.TestCase):
    def test_repository_source_playbook_registry_is_valid(self) -> None:
        self.assertEqual(CHECKER.check_source_playbooks(ROOT), [])

    def test_repository_has_active_kr_platform_service_playbook(self) -> None:
        registry = json.loads(
            (ROOT / "knowledge/general/source-playbook-index.json").read_text(encoding="utf-8")
        )
        entries = {
            entry["id"]: entry
            for entry in registry["playbooks"]
            if isinstance(entry, dict) and "id" in entry
        }
        self.assertEqual(entries["kr-platform-service"]["status"], "active")
        self.assertTrue((ROOT / entries["kr-platform-service"]["path"]).exists())

    def test_complete_temp_playbook_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prepare_temp_root(root)
            playbook_path = root / "knowledge/general/playbooks/kr-platform-service.md"
            playbook_path.write_text(valid_playbook_text(), encoding="utf-8")
            write_json(
                root / "knowledge/general/source-playbook-index.json",
                {
                    "version": "1.0",
                    "playbooks": [
                        {
                            "id": "kr-platform-service",
                            "jurisdiction": "KR",
                            "domain": "platform_service",
                            "path": "knowledge/general/playbooks/kr-platform-service.md",
                            "status": "active",
                        }
                    ],
                },
            )

            self.assertEqual(CHECKER.check_source_playbooks(root), [])

    def test_unregistered_playbook_file_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prepare_temp_root(root)
            (root / "knowledge/general/playbooks/kr-platform-service.md").write_text(
                valid_playbook_text(),
                encoding="utf-8",
            )
            write_json(root / "knowledge/general/source-playbook-index.json", {"version": "1.0", "playbooks": []})

            errors = CHECKER.check_source_playbooks(root)
            self.assertTrue(any("not registered" in error for error in errors), errors)

    def test_create_script_registers_draft_but_validation_requires_fill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prepare_temp_root(root)

            path, entry = CREATOR.create_playbook(
                root=root,
                jurisdiction="KR",
                domain="platform-service",
                title="KR Platform Service",
                owner="qa",
                last_reviewed="2026-05-06",
            )

            self.assertEqual(entry["id"], "kr-platform-service")
            self.assertTrue(path.exists())
            registry = json.loads(
                (root / "knowledge/general/source-playbook-index.json").read_text(encoding="utf-8")
            )
            self.assertEqual(registry["playbooks"][0]["id"], "kr-platform-service")

            errors = CHECKER.check_source_playbooks(root)
            self.assertTrue(any("unresolved template placeholder" in error for error in errors), errors)

    def test_create_script_rejects_duplicate_ids(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prepare_temp_root(root)
            CREATOR.create_playbook(
                root=root,
                jurisdiction="KR",
                domain="platform_service",
                title="KR Platform Service",
                last_reviewed="2026-05-06",
            )

            with self.assertRaises((FileExistsError, ValueError)):
                CREATOR.create_playbook(
                    root=root,
                    jurisdiction="KR",
                    domain="platform-service",
                    title="KR Platform Service",
                    last_reviewed="2026-05-06",
                )


if __name__ == "__main__":
    unittest.main()
