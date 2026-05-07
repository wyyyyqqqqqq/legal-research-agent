# General Quality Hardening Plan

This plan defines quality improvements to complete before running formal
`general-legal-research` parity comparisons.

The goal is to raise the merged agent's general-law research floor first, so
the later A/B comparison tests real parity rather than obvious missing
discipline.

## Objective

Strengthen `legal-research-agent` for pure general legal research in four
areas:

- general-law source planning;
- claim-level verification;
- current-law and effective-date discipline;
- contributor-friendly source playbook authoring.

These improvements should be implemented as compact skills, knowledge
checklists, and deterministic gates where possible. Avoid broad prompt bloat.

## Non-Goals

- Do not edit `../legal-agent-orchestrator` in this phase.
- Do not copy the full legacy `general-legal-research` prompt wholesale.
- Do not make token reduction a success criterion.
- Do not require live web/MCP research inside local deterministic tests.
- Do not replace human parity review with validators.

## Workstream 1: Source Playbook Authoring Scaffold

### Problem

General-law source coverage will need to grow over time. If every new source
playbook is hand-written without a scaffold, future contributors can easily
create inconsistent files, omit currentness checks, use broad domains, or forget
to register the playbook in the knowledge index.

### Target Behavior

Any contributor should be able to add a focused source playbook with one command,
fill in a known template, and run a deterministic validation check before the
playbook is used by the agent.

The scaffold should make the safe path easy:

- generate a stable playbook ID and file path;
- register the playbook in an index;
- require key sections;
- reject unresolved placeholders;
- enforce basic jurisdiction/domain vocabulary;
- make currentness and fallback behavior impossible to forget.

### Planned Files

Add:

```text
templates/source-playbook.example.md
knowledge/general/source-playbook-index.json
knowledge/general/playbooks/
scripts/create-source-playbook.py
scripts/check-source-playbooks.py
tests/test_source_playbooks.py
docs/source-playbook-authoring.md
```

Update:

```text
scripts/run-local-checks.py
README.md
docs/archive/plans/general-quality-hardening-plan.md
scripts/check-knowledge-coverage.py
tests/test_knowledge_coverage.py
```

### Template Shape

`templates/source-playbook.example.md` should include:

```text
# {Title}

## Metadata

- id:
- jurisdiction:
- domain:
- status:
- owner:
- last_reviewed:

## Scope

## Required Source Layers

## Official Source Entry Points

## Delegated Rule Checks

## Case Law Or Agency Decision Checks

## Currentness Checks

## Common Pitfalls

## Fallback Behavior

## Example Source Plan
```

### Registry Shape

Use a small JSON registry so scripts can validate it without parsing prose:

```json
{
  "version": "1.0",
  "playbooks": [
    {
      "id": "kr-platform-service",
      "jurisdiction": "KR",
      "domain": "platform_service",
      "path": "knowledge/general/playbooks/kr-platform-service.md",
      "status": "active"
    }
  ]
}
```

Allowed `status` values:

- `draft`
- `active`
- `deprecated`

Start with conservative jurisdiction vocabulary:

- `KR`
- `US`
- `EU`
- `JP`
- `UK`
- `MULTI`

Start with conservative general-domain vocabulary:

- `platform_service`
- `contracts_commercial`
- `administrative`
- `employment`
- `civil_liability`
- `consumer_ecommerce`
- `corporate`
- `tax`
- `general`

### Create Script

`scripts/create-source-playbook.py` should support:

```bash
python3 scripts/create-source-playbook.py \
  --jurisdiction KR \
  --domain platform_service \
  --title "KR Platform Service"
```

The script should:

- normalize ID to `{jurisdiction-lower}-{domain-kebab}`;
- create `knowledge/general/playbooks/{id}.md`;
- fill metadata and headings from the template;
- create the registry if missing;
- append the registry entry;
- fail on duplicate IDs or existing files;
- avoid overwriting user edits.

Optional future flags:

- `--status draft|active`;
- `--owner`;
- `--path`;
- `--force` only after explicit confirmation, not as a default.

### Validation Script

`scripts/check-source-playbooks.py` should validate:

- registry exists and has `version = 1.0`;
- every playbook ID is unique;
- every registry path exists;
- no playbook file is missing from the registry;
- jurisdiction/domain/status values use allowed vocabulary;
- required headings exist in order;
- `Required Source Layers`, `Currentness Checks`, and `Fallback Behavior` are
  non-empty;
- no unresolved template placeholders remain;
- playbook metadata matches registry values.

### Local Preflight Integration

Add a `source_playbooks` check to `scripts/run-local-checks.py`:

```bash
python3 scripts/check-source-playbooks.py
```

This should run before `knowledge_coverage`, because malformed playbooks should
fail independently from broader knowledge marker checks.

### Authoring Guide

`docs/source-playbook-authoring.md` should explain:

- when to add a playbook;
- when not to add one;
- how narrow a playbook should be;
- how to choose jurisdiction/domain;
- how to list official source entry points;
- how to write delegated-rule and currentness checks;
- how to describe fallback behavior;
- examples of good and bad source-layer entries;
- commands to run before submitting changes.

### Acceptance Criteria

- A contributor can create a draft playbook using the scaffold script.
- The created playbook is registered automatically.
- The validation script fails incomplete template output until required
  sections are filled.
- Existing local preflight includes the validation script.
- Documentation explains how to author and validate playbooks.

### Session 1 Status

Implemented.

Added:

```text
templates/source-playbook.example.md
knowledge/general/source-playbook-index.json
knowledge/general/playbooks/
scripts/create-source-playbook.py
scripts/check-source-playbooks.py
tests/test_source_playbooks.py
docs/source-playbook-authoring.md
```

Updated local preflight to run `source_playbooks` before `knowledge_coverage`.

## Workstream 2: General Law Source Playbook

### Problem

The merged agent has stronger game-regulation taxonomy than general-law
domain-specific source planning. Pure general work can fail if it misses a
required source layer, such as delegated rules, agency guidance, court
decisions, or jurisdiction-specific hierarchy.

### Target Behavior

Before answering a general-law question, the agent should identify:

- jurisdiction;
- legal domain;
- required source layers;
- source minimums;
- delegated rule or implementation layer;
- official guidance or enforcement layer;
- whether case law or administrative decisions are required;
- source limitations.

### Planned Files

Add or update:

```text
skills/general-law-source-playbook.md
knowledge/general/domain-source-checklist.md
knowledge/general/source-playbook-index.json
knowledge/general/playbooks/*.md
scripts/check-knowledge-coverage.py
tests/test_knowledge_coverage.py
skills/general-research.md
skills/source-collection.md
skills/legal-output-quality-standard.md
```

### Domain Checklist

Start with compact checklists for:

| Domain | Required source layers |
|---|---|
| KR platform/service | statute, enforcement decree/rule, regulator guidance, consumer/e-commerce guidance where relevant |
| KR contracts/commercial | Civil Act/Commercial Act, special statutes, Fair Trade Commission guidance where relevant |
| KR administrative | statute, decree, rule, notice/guideline, agency FAQ/enforcement position, sanction basis |
| KR employment | Labor Standards Act, decree/rule, Ministry guidance, cases/administrative interpretation where needed |
| KR civil liability | statute, Supreme Court/court cases when rule depends on interpretation, limitation/remedy source |
| KR consumer/e-commerce | Framework Act/E-Commerce Act/etc., decree/rule, KCA/FTC guidance, refund/cancellation rules |
| US general | federal/state split, statute/regulation, agency guidance, state law when controlling |
| EU general | regulation/directive distinction, member-state implementation, Commission/regulator guidance |
| JP general | statute/cabinet or ministerial orders, ministry guidance, regulator/source availability limits |
| UK general | statute/regulation, regulator guidance, case law where doctrine-driven |

### Minimum Gate

The agent should not mark an issue `high` confidence unless the required
source layers for that issue were checked or an explicit reason explains why
they were not required.

### Acceptance Criteria

- Source playbook authoring scaffold is in place before expanding many domain
  playbooks.
- Knowledge coverage guard requires the playbook and domain checklist markers.
- General research instructions require loading the playbook for `general`
  mode.
- Source collection instructions include a source-layer stop condition.
- Existing local preflight still passes.

### Session 2 Status

Implemented.

Added:

```text
skills/general-law-source-playbook.md
knowledge/general/domain-source-checklist.md
knowledge/general/playbooks/kr-platform-service.md
```

Updated:

```text
knowledge/general/source-playbook-index.json
skills/general-research.md
skills/source-collection.md
skills/legal-output-quality-standard.md
CLAUDE.md
knowledge/general/source-map.md
scripts/check-knowledge-coverage.py
tests/test_knowledge_coverage.py
tests/test_source_playbooks.py
```

The first active playbook is `kr-platform-service`.

## Workstream 3: Claim-Level Verification Loop

### Problem

The current gates require source IDs in key findings, issue blocks, short
answer, and rule sections. They do not fully verify that each legal proposition
is mapped to a specific claim, supporting source, pinpoint, and limitation.

### Target Behavior

Before final output, the agent should build an internal claim verification
table for material propositions.

Each claim should include:

- `claim_id`;
- legal proposition;
- issue reference;
- supporting `source_id`;
- pinpoint;
- support strength: `direct`, `indirect`, `background`, or `unsupported`;
- currentness status;
- limitation or caveat;
- confidence impact.

Only direct or clearly sufficient indirect support should carry a legal
conclusion. Background sources should not support controlling propositions.

### Planned Files

Add or update:

```text
skills/claim-verification-loop.md
templates/meta.example.json
skills/output-contract.md
skills/quality-check.md
skills/legal-output-quality-standard.md
scripts/evaluate-quality.py
tests/test_quality_evaluation.py
```

### Metadata Strategy

Keep this additive. Do not break older readers.

Recommended optional metadata field:

```json
{
  "claim_checks": [
    {
      "claim_id": "claim_001",
      "issue_id": "issue_001",
      "claim": "The operator must provide prior notice before changing material terms.",
      "authority_ids": ["src_001"],
      "support_strength": "direct",
      "currentness": "checked",
      "confidence_impact": "supports_medium_or_high",
      "limitation": "Confirm current regulator guidance before final client use."
    }
  ]
}
```

### Deterministic Gate

For local fixtures that include `claim_checks`, enforce:

- every `claim_id` is non-empty and unique;
- every `authority_ids[*]` exists in metadata sources;
- `support_strength` uses allowed vocabulary;
- `support_strength = background` or `unsupported` cannot support high
  confidence;
- each `key_findings[*]` source anchor should be represented by at least one
  claim check when claim checks are present;
- each issue with `confidence = high` should have at least one direct claim
  check.

### Acceptance Criteria

- Claim verification skill exists and is referenced by the output workflow.
- Optional `claim_checks` validation passes existing fixtures and fails
  targeted bad fixtures.
- No mandatory schema break.

### Session 4 Status

Implemented.

Added:

```text
skills/claim-verification-loop.md
```

Updated:

```text
skills/claim-spot-check.md
skills/output-contract.md
skills/legal-output-quality-standard.md
skills/quality-check.md
skills/result-memo-composition.md
CLAUDE.md
templates/meta.example.json
scripts/validate-output.py
scripts/evaluate-quality.py
tests/test_output_contract.py
tests/test_quality_evaluation.py
tests/fixtures/output/valid/legal-research-agent-meta.json
tests/fixtures/golden-set/kr_general_basic/legal-research-agent-meta.json
```

The `claim_checks` field remains additive. Fixtures without it continue to
validate, while fixtures that opt in must use known authority IDs and valid
support-strength values.

## Workstream 4: Currentness Gate

### Problem

General legal research can be substantively wrong if it relies on stale law,
pending amendments, repealed provisions, or unchecked effective dates. Existing
confidence alignment covers `temporal_status` gaps, but source-level currentness
discipline can be stronger.

### Target Behavior

Every controlling source should have a currentness status.

Recommended status vocabulary:

- `checked_current`;
- `effective_date_checked`;
- `pending_change`;
- `stale_or_superseded`;
- `not_checked`;
- `not_applicable`.

The result should visibly caveat any controlling proposition supported by a
source that is not currentness-checked.

### Planned Files

Add or update:

```text
skills/currentness-check.md
skills/source-grading.md
skills/source-collection.md
skills/result-memo-composition.md
skills/legal-output-quality-standard.md
templates/meta.example.json
scripts/validate-output.py
scripts/evaluate-quality.py
tests/test_output_contract.py
tests/test_quality_evaluation.py
```

### Metadata Strategy

Keep source metadata additive:

```json
{
  "sources": [
    {
      "id": "src_001",
      "title": "Act on ...",
      "grade": "A",
      "citation": "Article 12",
      "pinpoint": "Article 12(1)",
      "url_or_access": "official database",
      "currentness": {
        "status": "checked_current",
        "checked_as_of": "2026-05-06",
        "effective_date": null,
        "notes": "Official source checked for current version."
      }
    }
  ]
}
```

### Deterministic Gate

For local fixtures that include source `currentness`, enforce:

- `status` uses allowed vocabulary;
- `checked_as_of` is present for `checked_current` and
  `effective_date_checked`;
- high-confidence issues cannot rely only on sources with `not_checked`,
  `pending_change`, or `stale_or_superseded`;
- `pending_change`, `stale_or_superseded`, or `not_checked` on authority
  sources requires a `coverage_gaps` entry with type `temporal_status` or
  visible limiting language.

### Acceptance Criteria

- Currentness skill exists and is referenced by source collection and quality
  check workflow.
- Optional currentness metadata validation exists.
- Result structure guidance requires visible caveats for temporal uncertainty.
- Existing fixtures pass unless they opt into currentness metadata.

### Session 3 Status

Implemented.

Added:

```text
skills/currentness-check.md
```

Updated:

```text
skills/source-collection.md
skills/source-grading.md
skills/result-memo-composition.md
skills/legal-output-quality-standard.md
skills/quality-check.md
CLAUDE.md
templates/meta.example.json
scripts/validate-output.py
scripts/evaluate-quality.py
tests/test_output_contract.py
tests/test_quality_evaluation.py
tests/fixtures/output/valid/legal-research-agent-meta.json
tests/fixtures/golden-set/kr_general_basic/
```

The currentness gate remains additive. Fixtures without `sources[*].currentness`
continue to validate, while fixtures that opt in must use the status vocabulary
and confidence/caveat consequences.

## Suggested Implementation Order

1. Completed in Session 1: source playbook authoring scaffold.
2. Completed in Session 2: general-law source playbook and domain checklist.
3. Completed in Session 2: first active playbook, `kr-platform-service`.
4. Completed in Session 2: knowledge coverage guard updates.
5. Completed in Session 3: `currentness-check.md` and source currentness
   guidance.
6. Completed in Session 3: optional currentness validation.
7. Completed in Session 4: `claim-verification-loop.md`.
8. Completed in Session 4: optional `claim_checks` quality validation.
9. Completed in Session 5: update one general fixture to exercise source
   playbook, currentness, and claim-verification gates. Additional edge,
   fallback, and parity-promoted fixtures remain future expansion items after
   review.

## Quality Risks

- Overloading the base prompt with every source checklist.
  Mitigation: keep playbooks load-on-demand by mode/domain.
- Making optional metadata mandatory too early.
  Mitigation: validate fields only when present until fixtures are upgraded.
- Encouraging false precision in currentness.
  Mitigation: allow `not_checked` but force confidence/caveat consequences.
- Turning claim checks into bureaucracy.
  Mitigation: require claim checks for material propositions, not every
  sentence.

## Completion Definition

This hardening phase is complete when:

- source playbook authoring scaffold exists and is in local preflight;
- general source playbook exists and is covered by knowledge guard;
- currentness skill exists and optional metadata validation is tested;
- claim verification skill exists and optional metadata validation is tested;
- at least one general fixture exercises each new gate;
- `scripts/run-local-checks.py` passes;
- the merged agent is ready for the formal
  `docs/general-legacy-parity-plan.md` A/B phase.

## Session 5 Status

Implemented.

Session 5 performed integration cleanup rather than adding a new gate:

- README documents source playbook authoring, general-law source playbooks,
  currentness metadata, and claim checks.
- `docs/golden-set.md` documents the deterministic currentness and
  claim-verification gates.
- `kr_general_basic` exercises the general-law hardening path with
  source-layer guidance, `sources[*].currentness`, a `temporal_status` gap, and
  `claim_checks`.
- Local preflight passes.

This pre-parity hardening phase is complete. The next phase is the formal
`docs/general-legacy-parity-plan.md` A/B comparison against
`general-legal-research`; `../legal-agent-orchestrator` integration remains
deferred until those results are reviewed.
