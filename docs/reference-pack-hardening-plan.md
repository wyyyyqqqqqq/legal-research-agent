# Reference and Pack Hardening Plan

| | |
|---|---|
| **Status** | Implemented; optional catalog migration deferred |
| **Date** | 2026-05-26 |
| **Scope** | `references/`, `references/packs/`, specialist skills, and deterministic validators |
| **Primary risk addressed** | Dangling reference files and uneven specialist pack coverage |

## Purpose

The current repository has a meaningful reference-layer gap. Several specialist
skills point to reference files that do not exist, while other specialist skills
carry detailed drafting logic inline without a corresponding `references/packs/`
file. That creates three practical problems:

- a worker can follow a skill instruction into a missing file;
- detailed specialist behavior is uneven across topics;
- adding packs requires editing hardcoded validator constants, and no validator
  currently catches every stale internal reference.

This plan turns the reference layer into a governed, testable surface.

## Objective

Upgrade the reference and pack system so that:

1. every `references/*.md` and `references/packs/*.md` path mentioned by a skill
   or public doc exists, unless it is explicitly documented as legacy context;
2. every high-use specialist skill has either a compact self-contained workflow
   or a detailed pack with a clear loading rule;
3. validators detect missing, empty, stale, or unregistered reference material;
4. packs remain drafting and quality-control frameworks, not cached legal
   databases that can go stale silently.

## Non-Goals

- Do not ingest primary legal source text into `references/packs/`.
- Do not treat packs as authority for current law.
- Do not expand the main `CLAUDE.md` prompt with detailed pack content.
- Do not change the canonical two-file output contract.
- Do not edit `library/` ingestion behavior in this phase.
- Do not require live web or MCP calls in deterministic tests.

## Current Gap Inventory

### Missing Top-Level References

These files are referenced by existing skills but are absent:

```text
references/conflict-report-template.md
references/glossary-schema.md
```

Impact:

- `skills/specialists/conflict-detector.md` instructs workers to use a conflict
  template that does not exist.
- `skills/specialists/glossary-manager.md` instructs workers to read a glossary
  schema that does not exist.
- Neither gap is caught by `scripts/check-references-corpus.py` today because
  the expected reference set is hardcoded and incomplete.

### Stale Internal References

Known stale references to clean up or explicitly mark as legacy:

```text
references/legal-source-urls.md  # legacy path
.claude/skills/output-generator/references/mode-a-template.md  # legacy path
mode-b-template.md
```

Impact:

- `references/korean-law-reference.md` still points to the old
  `references/legal-source-urls.md` legacy path even though the source registry now
  lives in `legal_sources.yaml`.
- `references/legal-writing-formatting-guide.md` still names predecessor
  output-generator legacy path templates instead of the current
  `templates/output-modes/` files.

### Pack Coverage Gaps

Existing packs cover:

```text
antitrust-investigation-summary
api-acceptable-use-policy
cyber-law-compliance-summary
gambling-law-summary
ip-infringement-analysis
terms-of-service
```

High-value specialist skills without packs:

```text
privacy-law-updates
regulatory-summary
case-briefs
judgment-summary
```

Related specialist skills that need top-level references rather than packs:

```text
conflict-detector -> references/conflict-report-template.md
glossary-manager -> references/glossary-schema.md
```

### Validator Gaps

Current validators:

- `scripts/check-reference-packs.py` verifies only a hardcoded pack set and
  rejects extra packs unless the script is edited.
- `scripts/check-references-corpus.py` verifies only a hardcoded top-level
  reference set.
- No validator scans skills/docs for internal Markdown paths and verifies that
  the target files exist.
- No shared catalog declares owner skill, status, minimum size, or required
  headings for each reference artifact.

## Design Principles

1. **Compact skill, detailed pack.** A specialist skill should remain a fast
   router and checklist. Detailed tables, templates, pitfalls, and QC matrices
   belong in the pack.
2. **Packs are not law.** A pack can say what to verify and how to structure the
   answer. It must not present mutable legal rules as current authority.
3. **Every reference path must be auditable.** Internal Markdown links and
   inline paths should not rot silently.
4. **Deterministic gates first.** Missing files, unregistered packs, unresolved
   placeholders, and empty required sections should fail locally.
5. **Additive first pass.** Create missing files and update validators without
   broad workflow rewrites.

## Target File Set

Add:

```text
references/conflict-report-template.md
references/glossary-schema.md
references/packs/privacy-law-updates.md
references/packs/regulatory-summary.md
references/packs/case-briefs.md
references/packs/judgment-summary.md
scripts/check-reference-links.py
tests/test_reference_links.py
```

Update:

```text
skills/specialists/privacy-law-updates.md
skills/specialists/regulatory-summary.md
skills/specialists/case-briefs.md
skills/specialists/judgment-summary.md
scripts/check-reference-packs.py
scripts/check-references-corpus.py
scripts/check-knowledge-coverage.py
scripts/run-local-checks.py
tests/test_reference_packs.py
README.md
README.ko.md
references/korean-law-reference.md
references/legal-writing-formatting-guide.md
```

Optional after the first pass:

```text
references/reference-catalog.json
scripts/check-reference-catalog.py
tests/test_reference_catalog.py
```

The optional catalog is a Phase 2 governance improvement. The first pass can
keep the existing validator style by updating the hardcoded sets.

## Artifact Contracts

### `references/conflict-report-template.md`

Purpose:

- standardize conflict reporting across legal hierarchy, scope, recency,
  sanctions, and amendment/transitional conflicts.

Required sections:

```text
# Conflict Report Template
## Use When
## Conflict Summary
## Source Conflict Matrix
## Legal Hierarchy Analysis
## Currentness and Effective-Date Analysis
## Jurisdiction and Scope Analysis
## Resolution Path
## Research Re-Entry Plan
## Confidence Impact
## Final Answer Wording
## Citation Appendix
## Quality Checklist
```

Minimum content requirements:

- include a table for source-by-source conflict comparison;
- include Korean-specific rows for statute/decree delegation, local ordinance,
  old/new law transitional provisions, and general/special law conflicts;
- require `authority_ids` or equivalent source IDs for every conflict row;
- require a confidence downgrade when the conflict is unresolved and material;
- require re-entry to source collection for high-severity obligation or
  sanction conflicts.

### `references/glossary-schema.md`

Purpose:

- define the JSON shape used by `output/glossary/glossary-{jurisdiction}.json`;
- prevent inconsistent legal-term translations and unsourced definitions.

Required sections:

```text
# Glossary Schema
## Use When
## File Naming
## Top-Level Object
## Term Entry Fields
## Context Rule Fields
## Authority and Pinpoint Rules
## Korean Starter Glossary
## Validation Rules
## Example
## Quality Checklist
```

Core schema fields:

```json
{
  "schema_version": "1.0",
  "jurisdiction": "KR",
  "language_pair": "ko-en",
  "terms": [
    {
      "term": "시행령",
      "source_language": "ko",
      "preferred_translation": "Enforcement Decree",
      "definition": "Delegated presidential decree implementing a statute.",
      "authority_ids": ["src_001"],
      "pinpoints": ["..."],
      "status": "verified",
      "context_rules": []
    }
  ]
}
```

Minimum content requirements:

- define allowed `status` values: `verified`, `provisional`, `deprecated`;
- require source IDs and pinpoints for each definition;
- require context rules instead of overwriting a default translation;
- include the 15 Korean starter terms already named by
  `skills/specialists/glossary-manager.md`.

### `references/packs/privacy-law-updates.md`

Purpose:

- give `privacy-law-updates` a detailed currentness-heavy briefing framework.

Required sections:

```text
# Privacy Law Updates Reference Pack
## Quick Start
## Intake
## Development Taxonomy
## Jurisdiction Update Template
## Effective-Date and Deadline Tracker
## Enforcement Tracker
## Pending and Proposed Law Treatment
## Cross-Cutting Topic Matrix
## Source Minimums
## Output Quality Checklist
## Pitfalls
```

Minimum content requirements:

- distinguish enacted law, final rules, guidance, enforcement, court decisions,
  proposals, and consultations;
- require exact effective dates and compliance deadlines where available;
- require status labels for pending/proposed materials;
- require jurisdiction-first organization before cross-cutting synthesis;
- require privacy-sector carve-out checks such as children, health, financial,
  biometric, advertising, AI, and cross-border transfers.

### `references/packs/regulatory-summary.md`

Purpose:

- provide a document-type-aware framework for summarizing agency documents,
  rules, guidance, orders, and compliance frameworks.

Required sections:

```text
# Regulatory Summary Reference Pack
## Quick Start
## Intake
## Document-Type Matrix
## Metadata Table
## Provision Extraction Template
## Prior-Framework Delta
## Compliance Deadline Tracker
## Safe Harbors and Exemptions
## Enforcement and Penalties
## Comment or Appeal Posture
## Compliance Action Plan
## Output Quality Checklist
## Pitfalls
```

Minimum content requirements:

- distinguish final rule, proposed rule, interim final rule, guidance,
  enforcement order, no-action letter, advisory opinion, and framework;
- require pinpoint citations for every provision and action item;
- require procedural posture and deadline handling;
- forbid inferring agency intent where the document is ambiguous.

### `references/packs/case-briefs.md`

Purpose:

- make judicial opinion case briefs more reliable and less overbroad.

Required sections:

```text
# Case Briefs Reference Pack
## Quick Start
## Intake
## Case Metadata
## Procedural Posture
## Fact Extraction
## Issues Presented
## Holding and Disposition
## Reasoning and Rule Extraction
## Dicta and Limiting Language
## Concurring and Dissenting Opinions
## Significance
## Output Quality Checklist
## Pitfalls
```

Minimum content requirements:

- force narrow holding before broad principle;
- separate material facts from background facts;
- require quote discipline for legal standards;
- require missing-field treatment instead of inference;
- include non-US court adaptation notes.

### `references/packs/judgment-summary.md`

Purpose:

- make final judgment and appellate disposition summaries citation-ready.

Required sections:

```text
# Judgment Summary Reference Pack
## Quick Start
## Intake
## Judgment Metadata
## Procedural History
## Standards of Review
## Issues and Holdings Table
## Precedent Treatment
## Disposition and Remand Instructions
## Costs, Fees, Deadlines, and Conditions
## Practical Implications
## Key Citations
## Output Quality Checklist
## Pitfalls
```

Minimum content requirements:

- require standards of review where appellate posture is present;
- distinguish affirmed, reversed, vacated, remanded, dismissed, and modified;
- track precedent treatment: followed, distinguished, overruled, questioned;
- require separate handling of concurrence and dissent;
- avoid strategy advice unless clearly framed as practical implication.

## Validator Plan

### Update `scripts/check-reference-packs.py`

First pass:

- add the four new pack slugs to `EXPECTED_PACKS`;
- keep `MIN_BYTES = 1500` or raise to `2000` if new packs are substantial;
- add optional required-heading checks for all packs.

Better Phase 2:

- replace hardcoded `EXPECTED_PACKS` with `references/reference-catalog.json`;
- validate `kind = "pack"`, `owner_skill`, `status`, `min_bytes`, and
  `required_headings`.

### Update `scripts/check-references-corpus.py`

First pass:

- add `conflict-report-template` and `glossary-schema` to
  `EXPECTED_REFERENCES`;
- validate minimum size;
- optionally validate headings for the two new files.

Better Phase 2:

- read top-level references from `references/reference-catalog.json`;
- allow explicitly deprecated references only when no active skill points to
  them.

### Add `scripts/check-reference-links.py`

Purpose:

- scan project Markdown and Python files for internal paths that look like
  `references/*.md`, `references/packs/*.md`, `knowledge/*.md`,
  `templates/*.md`, or `.claude/.../*.md`;
- verify targets exist or are explicitly marked as legacy examples;
- fail on stale paths in active instruction files.

Initial scan scope:

```text
CLAUDE.md
README.md
README.ko.md
docs/
skills/
knowledge/
references/
templates/
scripts/
```

Ignore rules:

- ignore paths inside historical archived plans unless `--include-archive` is
  passed;
- ignore URLs;
- ignore paths in fenced code blocks only if they are examples and cannot be
  resolved by design;
- permit explicit markers such as `[legacy path]` or `[historical reference]`
  in archived context.

Add the check to `scripts/run-local-checks.py` after `references_corpus`.

### Update `scripts/check-knowledge-coverage.py`

Add markers for:

- `references/conflict-report-template.md`;
- `references/glossary-schema.md`;
- the new pack-loading lines in the four specialist skills;
- the new `reference_links` local check entry.

## Skill Integration Plan

Update these skills to match the existing pack pattern:

```text
skills/specialists/privacy-law-updates.md
skills/specialists/regulatory-summary.md
skills/specialists/case-briefs.md
skills/specialists/judgment-summary.md
```

Each update should:

- say the skill is the compact checklist;
- load the matching pack only when drafting, tailoring, or quality-checking the
  relevant deliverable;
- preserve current quick-start content;
- point to the pack in a `Reference Pack` or `Detailed Pack` section;
- avoid copying pack tables inline.

Do not add pack-loading requirements to every use of the skill. Loading should
be conditional on drafting or QC complexity so simple direct lookups stay light.

## Implementation Sequence

### Phase 0: Inventory and Link Cleanup

- [x] Confirm all active skill references to `references/*.md` and
  `references/packs/*.md`.
- [x] Fix `references/korean-law-reference.md` to point from
  `references/legal-source-urls.md` legacy path to `legal_sources.yaml`.
- [x] Fix `references/legal-writing-formatting-guide.md` to point to current
  output-mode templates.
- [x] Decide whether archived plans should be excluded from link validation by
  default.

### Phase 1: Missing Top-Level References

- [x] Add `references/conflict-report-template.md`.
- [x] Add `references/glossary-schema.md`.
- [x] Update `scripts/check-references-corpus.py`.
- [x] Add or update tests for top-level reference completeness.

### Phase 2: Specialist Packs

- [x] Add `references/packs/privacy-law-updates.md`.
- [x] Add `references/packs/regulatory-summary.md`.
- [x] Add `references/packs/case-briefs.md`.
- [x] Add `references/packs/judgment-summary.md`.
- [x] Update four specialist skills with pack-loading rules.
- [x] Update `scripts/check-reference-packs.py`.
- [x] Run `python3 scripts/check-reference-packs.py`.

### Phase 3: Link and Catalog Governance

- [x] Add `scripts/check-reference-links.py`.
- [x] Add `tests/test_reference_links.py`.
- [x] Add `reference_links` to `scripts/run-local-checks.py`.
- [x] Update `scripts/check-knowledge-coverage.py`.
- [ ] Optional: add `references/reference-catalog.json`.
- [ ] Optional: migrate `check-reference-packs.py` and
  `check-references-corpus.py` to read the catalog.

### Phase 4: Documentation

- [x] Update `README.md` architecture or repository tree to mention top-level
  references and specialist packs.
- [x] Mirror the relevant README update in `README.ko.md`.
- [x] Add a short note in `docs/source-playbook-authoring.md` or a new
  reference-authoring section explaining when to create a pack.
- [ ] Move this plan to `docs/archive/plans/` after the optional catalog
  decision is made.

### Phase 5: Verification

Run:

```bash
python3 scripts/check-references-corpus.py
python3 scripts/check-reference-packs.py
python3 scripts/check-reference-links.py
python3 -m unittest tests/test_reference_packs.py tests/test_reference_links.py
python3 scripts/run-local-checks.py
```

If full local checks are too slow, at minimum run the first four commands and
record any skipped checks in the implementation summary.

## Acceptance Criteria

The update is complete when:

- no active skill points to a missing reference file;
- the six existing packs and four new packs pass catalog validation;
- `conflict-detector` and `glossary-manager` have real referenced artifacts;
- stale predecessor paths are removed or explicitly marked historical;
- local validators fail on newly introduced dangling reference paths;
- specialist skills stay compact and delegate only detailed drafting/QC content
  to packs;
- all added files are covered by deterministic tests or marker checks.

## Risks and Mitigations

| Risk | Mitigation |
|---|---|
| Pack content becomes stale legal guidance | Keep packs procedural and citation-oriented; require live official sources for law. |
| Prompt bloat | Keep skill edits compact and load packs only on drafting/QC need. |
| Validator false positives | Exclude archived plans by default and allow explicit legacy markers. |
| Duplicate case/judgment logic | Keep `case-briefs` focused on opinion study and `judgment-summary` focused on final order/disposition consequences. |
| Hardcoded validator drift continues | Add catalog migration as Phase 2 if pack count keeps growing. |

## Recommended PR Breakdown

1. **PR 1: Repair dangling references**
   - Add `conflict-report-template.md` and `glossary-schema.md`.
   - Fix stale internal paths.
   - Update corpus validator.

2. **PR 2: Add four specialist packs**
   - Add privacy, regulatory, case-brief, and judgment packs.
   - Update specialist skill pack-loading rules.
   - Update pack validator.

3. **PR 3: Add link validator**
   - Add `check-reference-links.py`.
   - Add tests and local-check integration.
   - Update knowledge coverage markers.

4. **PR 4: Optional catalog migration**
   - Add `references/reference-catalog.json`.
   - Move pack/reference validators off hardcoded sets.

## Implementation Notes

- Keep headings stable because validators and future agents can rely on them.
- Use tables for repeatable QC where possible.
- Prefer source IDs such as `src_001` or `authority_ids` in templates so the
  packs align with the existing metadata and claim-verification model.
- Avoid jurisdiction-specific legal conclusions unless phrased as examples that
  must be verified against live primary sources.
- Preserve the distinction between `knowledge/` and `references/`:
  `knowledge/` orients research mode and domain source planning;
  `references/` holds reusable drafting, verification, schema, and template
  material.
