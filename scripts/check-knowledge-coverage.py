#!/usr/bin/env python3
"""Check that core quality and source-planning files keep required coverage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_MARKERS: dict[str, list[str]] = {
    "CLAUDE.md": [
        "jurisdiction-source-playbook.md",
        "general-law-source-playbook.md",
        "currentness-check.md",
        "claim-verification-loop.md",
        "Quality Supremacy",
        "Privacy Handoff",
    ],
    "skills/general-research.md": [
        "general-law-source-playbook.md",
        "domain-source-checklist.md",
        "source-playbook-index.json",
        "Jurisdiction Discipline",
        "supplementary provisions",
        "coverage_gaps",
    ],
    "skills/general-law-source-playbook.md": [
        "Source Playbook Selection",
        "Source Layer Plan",
        "Confidence Rule",
        "Stop Conditions",
    ],
    "skills/game-regulation-research.md": [
        "comparison_matrix",
        "co_running_agents",
        "jurisdiction-source-playbook.md",
    ],
    "skills/jurisdiction-source-playbook.md": [
        "Jurisdiction Profile",
        "Source Minimums",
        "Stop Conditions",
    ],
    "skills/result-memo-composition.md": [
        "Required Sections",
        "Route Context",
        "Issue Blocks",
        "Every metadata source",
        "currentness or effective-date note",
        "claim-verification limitation",
        "temporal",
        "Coverage Gaps",
    ],
    "skills/legal-writing-formatter.md": [
        "standalone_markdown",
        "handoff_packet",
        "docx_ready_markdown",
        "Transformation Workflow",
        "docs/standalone-workflow.md",
        "Do not load both profiles",
    ],
    "docs/standalone-workflow.md": [
        "Artifact Layout",
        "Naming Rules",
        "standalone-deliverable-manifest.json",
        "scripts/render-docx.py",
        "generated_and_extracted",
        "Citation Audit Integration",
        "Completion Criteria",
    ],
    "skills/source-collection.md": [
        "Source Minimum Enforcement",
        "Source-Layer Stop Condition",
        "general-law-source-playbook.md",
        "currentness-check.md",
        "temporal_status",
        "Similar-Statute Guard",
    ],
    "skills/source-grading.md": [
        "currentness",
        "checked_current",
        "currentness-check.md",
        "Source Laundering",
    ],
    "skills/claim-spot-check.md": [
        "Claim Registry",
        "claim-verification-loop.md",
        "Source Laundering Patterns",
    ],
    "skills/claim-verification-loop.md": [
        "Material Claims",
        "Metadata Shape",
        "Support Strength",
        "High-Confidence Rule",
        "Key Finding Rule",
    ],
    "skills/currentness-check.md": [
        "Status Vocabulary",
        "Metadata Shape",
        "Confidence Consequences",
        "Stop Conditions",
    ],
    "skills/quality-check.md": [
        "claim_checks",
        "claim_checks[*].authority_ids[*]",
        "direct claim check",
        "currentness-check.md",
        "temporal_status",
        "not_checked",
        "pending_change",
    ],
    "skills/legal-output-quality-standard.md": [
        "Non-Negotiable Standard",
        "claim-verification-loop.md",
        "claim_checks",
        "currentness-check.md",
        "stale_or_superseded",
        "selected domain checklist or active source playbook minimums",
        "Local Quality Gate",
    ],
    "skills/output-contract.md": [
        "Optional Claim Checks",
        "claim_checks",
        "support_strength",
        "claim_verification",
    ],
    "skills/specialists/privacy-law-updates.md": [
        "references/packs/privacy-law-updates.md",
        "Reference Pack",
        "development taxonomy",
    ],
    "skills/specialists/regulatory-summary.md": [
        "references/packs/regulatory-summary.md",
        "Reference Pack",
        "document-type",
    ],
    "skills/specialists/case-briefs.md": [
        "references/packs/case-briefs.md",
        "Reference Pack",
        "narrow holdings",
    ],
    "skills/specialists/judgment-summary.md": [
        "references/packs/judgment-summary.md",
        "Reference Pack",
        "standards of review",
    ],
    "references/conflict-report-template.md": [
        "Source Conflict Matrix",
        "Legal Hierarchy Analysis",
        "Korean-Specific Conflict Patterns",
        "Confidence Impact",
    ],
    "references/glossary-schema.md": [
        "Top-Level Object",
        "Term Entry Fields",
        "Context Rule Fields",
        "Korean Starter Glossary",
    ],
    "references/packs/privacy-law-updates.md": [
        "Development Taxonomy",
        "Effective-Date and Deadline Tracker",
        "Pending and Proposed Law Treatment",
        "Source Minimums",
    ],
    "references/packs/regulatory-summary.md": [
        "Document-Type Matrix",
        "Provision Extraction Template",
        "Compliance Deadline Tracker",
        "Safe Harbors and Exemptions",
    ],
    "references/packs/case-briefs.md": [
        "Fact Extraction",
        "Holding and Disposition",
        "Dicta and Limiting Language",
        "Concurring and Dissenting Opinions",
    ],
    "references/packs/judgment-summary.md": [
        "Standards of Review",
        "Issues and Holdings Table",
        "Disposition and Remand Instructions",
        "Practical Implications",
    ],
    "references/reference-catalog.json": [
        "\"version\": \"1.0\"",
        "\"artifacts\"",
        "\"conflict-report-template\"",
        "\"privacy-law-updates\"",
    ],
    "scripts/check-reference-catalog.py": [
        "CATALOG_PATH",
        "ALLOWED_KINDS",
        "discover_reference_files",
        "deprecated_pointed_to_by_active_skills",
    ],
    "scripts/create-reference-artifact.py": [
        "create_reference_artifact",
        "status\": \"draft\"",
        "check-reference-catalog.py",
    ],
    "scripts/check-reference-links.py": [
        "MARKDOWN_LINK_RE",
        "VALIDATED_PREFIXES",
        "extract_reference_targets",
    ],
    "scripts/check-glossary-files.py": [
        "ALLOWED_STATUSES",
        "authority_ids",
        "pinpoints",
        "context_rules",
    ],
    "tests/fixtures/glossary/valid/glossary-kr.json": [
        "\"schema_version\": \"1.0\"",
        "\"authority_ids\"",
        "\"context_rules\"",
    ],
    "scripts/run-local-checks.py": [
        "\"reference_catalog\"",
        "\"reference_links\"",
        "\"glossary_files\"",
        "scripts/check-reference-catalog.py",
        "scripts/check-reference-links.py",
        "scripts/check-glossary-files.py",
    ],
    "templates/source-playbook.example.md": [
        "## Required Source Layers",
        "## Currentness Checks",
        "## Fallback Behavior",
    ],
    "docs/source-playbook-authoring.md": [
        "create-source-playbook.py",
        "check-source-playbooks.py",
        "source-playbook-index.json",
        "Fallback Behavior",
    ],
    "knowledge/general/source-playbook-index.json": [
        "\"version\": \"1.0\"",
        "\"playbooks\"",
        "\"kr-platform-service\"",
    ],
    "knowledge/general/domain-source-checklist.md": [
        "KR platform/service",
        "US general",
        "EU general",
        "Confidence Consequences",
    ],
    "knowledge/general/playbooks/kr-platform-service.md": [
        "Required Source Layers",
        "Official Source Entry Points",
        "Currentness Checks",
        "Fallback Behavior",
    ],
    "knowledge/general/source-map.md": [
        "Domain Playbooks",
        "domain-source-checklist.md",
        "United States",
        "European Union",
        "Japan",
        "Minimum Coverage By Deliverable",
    ],
    "knowledge/game-regulation/source-map.md": [
        "Korea",
        "Japan",
        "EU",
        "United States",
    ],
    "knowledge/legal-writing/formatter-index.md": [
        "Korean legal research memo",
        "English legal research memo",
        "DOCX-ready Markdown",
        "Do not load both profiles",
    ],
    "knowledge/legal-writing/docx-ready-markdown-profile.md": [
        "DOCX-Ready Markdown",
        "scripts/render-docx.py",
        "MVP DOCX rendering",
        "Source Appendix",
        "DOCX Honesty Rule",
    ],
    "knowledge/legal-writing/ko-formatter-profile.md": [
        "합니다",
        "쟁점",
        "Section Drafting Rules",
        "출처",
        "Source Coverage Gap",
    ],
    "knowledge/legal-writing/en-formatter-profile.md": [
        "Executive Summary",
        "Issues Presented",
        "Section Drafting Rules",
        "Sources",
        "Source Coverage Gap",
    ],
    "docs/en/how-to-use.md": [
        "## Prerequisites",
        "## Quick Start",
        "## Personal Configuration",
        "## Research Modes",
        "## Output Modes",
        "## Packaging Modes",
        "## Citation Audit",
        "## Local-Only vs MCP-Connected",
        "## Tips",
    ],
    "docs/ko/how-to-use.md": [
        "## Prerequisites",
        "## Quick Start",
        "## Personal Configuration",
        "## Research Modes",
        "## Output Modes",
        "## Packaging Modes",
        "## Citation Audit",
        "## Local-Only vs MCP-Connected",
        "## Tips",
    ],
    "docs/en/disclaimer.md": [
        "## Personal Project",
        "## Not Legal Advice",
        "## AI Limitations",
        "## Data Handling",
        "## No Warranty",
        "## Scope of Responsibility",
        "Fabricate legal authorities",
        "Conflate jurisdictions",
        "Invent citations",
    ],
    "docs/ko/disclaimer.md": [
        "## Personal Project",
        "## Not Legal Advice",
        "## AI Limitations",
        "## Data Handling",
        "## No Warranty",
        "## Scope of Responsibility",
    ],
    "docs/en/mcp-setup-guide.md": [
        "## Korean Law MCP Server",
        "## Configuration",
        "## Verification",
        "## Degradation Behavior",
        "## Troubleshooting",
        "mcp__claude_ai_Korean-law__",
        "mcp_unavailable",
    ],
    "docs/ko/mcp-setup-guide.md": [
        "## Korean Law MCP Server",
        "## Configuration",
        "## Verification",
        "## Degradation Behavior",
        "## Troubleshooting",
    ],
    "docs/citation-audit.md": [
        "## Invocation Contexts",
        "## Output Artifacts",
        "## Format Support Matrix",
        "## Detailed Status Model",
        "## Korean-Law MCP Degradation",
        "## 한국어 요약",
        "verified",
        "contradicted",
        "unsupported",
        "source_unavailable",
        "verifier_unavailable",
        "not_a_legal_claim",
    ],
    "docs/release-process.md": [
        "## Pre-Release Checklist",
        "## Version Tagging",
        "## Release Notes",
        "## Post-Release",
        "scripts/run-local-checks.py",
        "scripts/measure-prompt-footprint.py",
        "scripts/compare-token-runs.py",
        "scripts/check-reference-catalog.py",
        "reference-catalog report",
    ],
}


def check_markers(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for relative_path, markers in REQUIRED_MARKERS.items():
        path = root / relative_path
        if not path.exists():
            errors.append(f"{relative_path}: missing file")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative_path}: missing marker {marker!r}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    errors = check_markers(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: knowledge coverage markers present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
