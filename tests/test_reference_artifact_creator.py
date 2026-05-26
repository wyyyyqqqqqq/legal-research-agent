#!/usr/bin/env python3
"""Validate reference artifact authoring scaffold."""

from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CREATOR_PATH = REPO_ROOT / "scripts" / "create-reference-artifact.py"
CATALOG_CHECKER_PATH = REPO_ROOT / "scripts" / "check-reference-catalog.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CREATOR = load_module("create_reference_artifact", CREATOR_PATH)
CATALOG_CHECKER = load_module("check_reference_catalog_for_creator", CATALOG_CHECKER_PATH)


def prepare_root(root: Path) -> None:
    shutil.copytree(REPO_ROOT / "references", root / "references")
    shutil.copytree(REPO_ROOT / "skills", root / "skills")


class ReferenceArtifactCreatorTest(unittest.TestCase):
    def test_create_pack_registers_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prepare_root(root)

            path, entry = CREATOR.create_reference_artifact(
                root=root,
                kind="pack",
                artifact_id="ai-governance-briefing",
                title="AI Governance Briefing",
                owner_skill="privacy-law-updates",
            )

            self.assertEqual(path.relative_to(root), Path("references/packs/ai-governance-briefing.md"))
            self.assertEqual(entry["status"], "draft")
            self.assertEqual(entry["owner_skill"], "privacy-law-updates")
            self.assertEqual(CATALOG_CHECKER.check(root), [])

    def test_create_reference_registers_draft(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prepare_root(root)

            path, entry = CREATOR.create_reference_artifact(
                root=root,
                kind="reference",
                artifact_id="memo-sanity-check",
                title="Memo Sanity Check",
            )

            self.assertEqual(path.relative_to(root), Path("references/memo-sanity-check.md"))
            self.assertEqual(entry["kind"], "reference")
            self.assertEqual(CATALOG_CHECKER.check(root), [])

    def test_duplicate_id_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prepare_root(root)

            with self.assertRaises((FileExistsError, ValueError)):
                CREATOR.create_reference_artifact(
                    root=root,
                    kind="reference",
                    artifact_id="glossary-schema",
                )

    def test_missing_owner_skill_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            prepare_root(root)

            with self.assertRaises(ValueError):
                CREATOR.create_reference_artifact(
                    root=root,
                    kind="pack",
                    artifact_id="missing-owner-pack",
                    owner_skill="does-not-exist",
                )


if __name__ == "__main__":
    unittest.main()
