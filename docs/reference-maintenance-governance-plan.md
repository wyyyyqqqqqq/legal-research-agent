# Reference Maintenance Governance Plan

| | |
|---|---|
| **Status** | Implemented |
| **Date** | 2026-05-26 |
| **Depends on** | `docs/reference-pack-hardening-plan.md` |
| **Scope** | Reference cataloging, validators, authoring workflow, fixtures, and release hygiene |

## Purpose

The reference hardening work closed the immediate quality gap: missing
references were added, specialist packs were expanded, stale paths were fixed,
and active internal reference links are now checked.

The next maintenance risk is slower and quieter: as references and packs grow,
contributors must update several hardcoded locations by hand. That is workable
for 10 packs and 7 top-level references, but it will become brittle when the
catalog expands.

This plan moves the reference layer from "validated by scattered constants" to
"governed by a single catalog and small authoring tools."

## Objective

Improve long-term maintainability so that:

1. reference and pack metadata live in one machine-readable catalog;
2. validators read the catalog instead of duplicating expected file lists;
3. adding a new reference or pack has a guided scaffold;
4. tests cover negative cases, schema drift, and stale links;
5. documentation explains the lifecycle from draft to active to deprecated;
6. release checks can tell whether reference changes are intentional.

## Non-Goals

- Do not change the current legal-research workflow or output contract.
- Do not add live web/MCP checks to local deterministic validation.
- Do not store current legal source text in packs.
- Do not require a database or external service.
- Do not build a full docs site generator.
- Do not move existing reference files unless the catalog migration requires a
  clearly mechanical path update.

## Current State

After the hardening pass:

- top-level references are validated by `scripts/check-references-corpus.py`;
- specialist packs are validated by `scripts/check-reference-packs.py`;
- active internal Markdown paths are validated by `scripts/check-reference-links.py`;
- `scripts/run-local-checks.py` includes a `reference_links` gate;
- reference-specific markers are covered by `scripts/check-knowledge-coverage.py`.

Remaining maintenance friction:

- expected references and expected packs are still hardcoded in two validators;
- required headings are also embedded in validator code;
- there is no single place to see owner skill, artifact type, lifecycle status,
  min size, and required headings;
- adding a pack requires manual edits to the pack, skill, validator, docs, and
  tests;
- the link checker intentionally stays narrow and does not validate all
  ordinary Markdown links;
- there is no fixture proving glossary output shape beyond the prose schema.

## Design Principles

1. **One catalog, many checks.** Store artifact metadata once and let validators
   consume it.
2. **Procedural packs stay procedural.** The catalog should describe how to
   validate a pack, not turn it into legal authority.
3. **Scaffold the boring parts.** New references should start with known
   headings, metadata, and validator registration.
4. **Lifecycle is explicit.** A reference is `draft`, `active`, or
   `deprecated`; validators treat each status differently.
5. **Negative tests matter.** Validators should prove they fail on missing files,
   duplicate IDs, bad headings, stale links, and invalid statuses.
6. **Keep local checks fast.** The whole governance layer should stay file-based
   and deterministic.

## Target Architecture

### Reference Catalog

Add a single catalog:

```text
references/reference-catalog.json
```

Proposed shape:

```json
{
  "version": "1.0",
  "artifacts": [
    {
      "id": "conflict-report-template",
      "kind": "reference",
      "path": "references/conflict-report-template.md",
      "status": "active",
      "owner_skill": "conflict-detector",
      "min_bytes": 1000,
      "required_headings": [
        "# Conflict Report Template",
        "## Source Conflict Matrix",
        "## Quality Checklist"
      ]
    },
    {
      "id": "privacy-law-updates",
      "kind": "pack",
      "path": "references/packs/privacy-law-updates.md",
      "status": "active",
      "owner_skill": "privacy-law-updates",
      "min_bytes": 1500,
      "required_headings": [
        "# Privacy Law Updates Reference Pack",
        "## Development Taxonomy",
        "## Output Quality Checklist"
      ]
    }
  ]
}
```

Allowed fields:

| Field | Required | Notes |
|---|---:|---|
| `id` | Yes | Stable slug, usually file stem. |
| `kind` | Yes | `reference` or `pack`. Optional future: `schema`, `template`, `legacy`. |
| `path` | Yes | Repository-relative path. |
| `status` | Yes | `draft`, `active`, or `deprecated`. |
| `owner_skill` | No | Specialist or workflow skill that loads it. |
| `owner_doc` | No | Public doc that owns it when no skill does. |
| `min_bytes` | Yes | Size floor to catch placeholders. |
| `required_headings` | Yes | Ordered or unordered heading markers. |
| `notes` | No | Human-readable caveat. |

Status behavior:

| Status | Validator behavior |
|---|---|
| `draft` | File may exist and headings must pass, but no active skill may require it for final output. |
| `active` | File must exist, pass size and heading checks, and link checker must resolve paths. |
| `deprecated` | File may remain, but no active skill should point to it unless marked legacy. |

### Unified Validator

Add:

```text
scripts/check-reference-catalog.py
tests/test_reference_catalog.py
```

Responsibilities:

- validate catalog JSON shape;
- require unique IDs and paths;
- require allowed `kind` and `status`;
- verify every catalog path exists;
- verify every `references/*.md` and `references/packs/*.md` file appears in the
  catalog unless explicitly ignored;
- verify min size and required headings;
- verify `owner_skill` exists when provided;
- verify active skills do not point to deprecated artifacts.

Migration choices:

- Option A: keep `check-references-corpus.py` and `check-reference-packs.py` as
  wrappers that call catalog logic with `kind = reference` or `kind = pack`.
- Option B: replace both local-check entries with one `reference_catalog` gate.

Recommended path: Option A for backward compatibility in the first PR, then
Option B after one release cycle.

### Authoring Scaffold

Add a small script:

```text
scripts/create-reference-artifact.py
```

Example:

```bash
python3 scripts/create-reference-artifact.py \
  --kind pack \
  --id ai-governance-briefing \
  --owner-skill privacy-law-updates \
  --title "AI Governance Briefing"
```

Script behavior:

- create `references/packs/{id}.md` or `references/{id}.md`;
- insert a standard title and required starter headings;
- add a catalog entry with `status = draft`;
- fail on duplicate ID or existing file;
- print next steps: fill headings, update skill load rule, run validators.

Future template file intentionally missing until implementation:

```text
templates/reference-artifact.example.md  # intentionally missing until implementation
```

### Glossary Fixture Coverage

Add deterministic fixtures:

```text
tests/fixtures/glossary/valid/glossary-kr.json
tests/fixtures/glossary/invalid-missing-source/glossary-kr.json
tests/fixtures/glossary/invalid-bad-status/glossary-kr.json
scripts/check-glossary-files.py
tests/test_glossary_files.py
```

Validator responsibilities:

- enforce `references/glossary-schema.md` shape;
- require `schema_version`, `jurisdiction`, `language_pair`, and `terms`;
- require `authority_ids` and `pinpoints` for every term and context rule;
- reject unknown statuses;
- reject duplicate terms unless context rules distinguish them.

This gives the glossary schema teeth without requiring runtime legal research.

### Link Checker Expansion

Current `check-reference-links.py` focuses on active internal Markdown reference
paths. That is the right first pass.

Next improvements:

- parse standard Markdown links like `[label](references/conflict-report-template.md)`;
- parse angle-wrapped paths with spaces;
- detect anchors only when the target file exists;
- report broken links with line numbers and suggested fixes;
- keep `docs/archive/` excluded by default;
- allow explicit legacy markers only for historical or intentionally missing
  examples.

Avoid validating external URLs in this checker. External link freshness belongs
in a separate optional release audit, not local preflight.

### Reference Change Report

Add a lightweight report mode:

```bash
python3 scripts/check-reference-catalog.py --report-json reports/reference-catalog.json
```

Report fields:

```json
{
  "total": 17,
  "by_kind": {"reference": 7, "pack": 10},
  "by_status": {"active": 17},
  "deprecated_pointed_to_by_active_skills": [],
  "uncataloged_files": [],
  "missing_required_headings": []
}
```

Use the report in release notes when reference-layer changes are substantial.

## Implementation Sequence

### Phase 1: Catalog Introduction

- [x] Add `references/reference-catalog.json`.
- [x] Populate all current top-level references and packs.
- [x] Add `scripts/check-reference-catalog.py`.
- [x] Add `tests/test_reference_catalog.py`.
- [x] Keep existing corpus and pack validators unchanged until catalog check
  passes.
- [x] Run catalog check and full preflight.

### Phase 2: Validator Consolidation

- [x] Refactor `scripts/check-references-corpus.py` to read catalog entries with
  `kind = reference`.
- [x] Refactor `scripts/check-reference-packs.py` to read catalog entries with
  `kind = pack`.
- [x] Remove duplicated `EXPECTED_REFERENCES`, `EXPECTED_PACKS`, and heading
  constants from those scripts.
- [x] Update tests to assert wrapper behavior still works.
- [x] Add negative fixture tests for missing file, duplicate ID, bad status, and
  missing heading.

### Phase 3: Authoring Tooling

- [x] Add `scripts/create-reference-artifact.py`.
- [x] Add a starter template or inline template constants.
- [x] Add tests for draft creation, duplicate rejection, and catalog update.
- [x] Update `docs/source-playbook-authoring.md` or create a dedicated
  reference authoring section.
- [x] Update README / README.ko with the new command.

### Phase 4: Glossary Validation

- [x] Add valid and invalid glossary fixtures.
- [x] Add `scripts/check-glossary-files.py`.
- [x] Add `tests/test_glossary_files.py`.
- [x] Add `glossary_files` to `scripts/run-local-checks.py`.
- [x] Add knowledge coverage markers for the glossary validator and fixtures.

### Phase 5: Link Checker Upgrade

- [x] Extend `scripts/check-reference-links.py` to parse Markdown links in
  addition to inline reference paths.
- [x] Add fixtures for valid links, missing links, archived links, and explicit
  legacy markers.
- [x] Keep external URLs out of scope.
- [x] Confirm full preflight remains fast.

### Phase 6: Release Hygiene

- [x] Add `--report-json` to the catalog validator.
- [x] Mention reference-catalog reports in `docs/release-process.md`.
- [x] Add a release checklist item: reference changes have catalog entries,
  owner skills, status, and validation reports.
- [x] Decide whether implemented maintenance plans should move to
  `docs/archive/plans/` (left in `docs/` for now as current governance
  reference).

## Acceptance Criteria

This maintenance upgrade is complete when:

- every active reference and pack is represented in `references/reference-catalog.json`;
- corpus and pack validators no longer duplicate catalog lists;
- adding a new reference can be done through a scaffold command;
- glossary fixtures prove the schema can be validated;
- link checker covers both inline paths and normal Markdown links;
- full local preflight passes with the new catalog, glossary, and link checks;
- release docs explain how to review reference-layer changes.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Catalog becomes another file contributors forget | Make validators fail on uncataloged `references/*.md` and `references/packs/*.md`. |
| Too much schema ceremony slows small updates | Keep required fields minimal; let optional fields stay optional. |
| Draft files break local checks | Allow `draft` status but require basic file and heading validity. |
| Deprecated artifacts linger forever | Add report output and release checklist visibility. |
| Link checker false positives | Keep archive excluded by default and allow explicit legacy markers. |
| Authoring script over-engineers simple files | Script should generate only skeleton, catalog entry, and next-step hints. |

## Recommended PR Breakdown

1. **PR 1: Catalog foundation**
   - Add catalog, catalog validator, and tests.
   - Keep old validators intact.

2. **PR 2: Validator consolidation**
   - Make corpus and pack validators read the catalog.
   - Add negative tests.

3. **PR 3: Authoring scaffold**
   - Add create script and docs.

4. **PR 4: Glossary fixtures**
   - Add glossary validator, fixtures, tests, and local-check integration.

5. **PR 5: Link checker expansion and release hygiene**
   - Expand Markdown link parsing.
   - Add report mode and release-process notes.

## Notes for Future Implementers

- Prefer catalog data over new hardcoded constants.
- Keep IDs stable; changing an ID should be treated like a migration.
- Do not catalog `library/` ingested files; that directory is user data.
- Do not require live source currentness in reference-pack validation.
- Keep every generated artifact deterministic so tests can run without network
  or MCP access.
