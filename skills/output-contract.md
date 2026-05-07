---
name: output-contract
description: Defines the two required output files and their metadata schema for orchestrator-compatible runs.
disable-model-invocation: true
---

# Output Contract

The agent must write exactly two files:

```text
{OUTPUT_DIR}/legal-research-agent-result.md
{OUTPUT_DIR}/legal-research-agent-meta.json
```

## Required Metadata Fields

- `meta_version`
- `summary`
- `research_mode`
- `mode_source`
- `active_profile`
- `orchestrator_route_mode`
- `fallback_reason`
- `classification_warnings`
- `co_running_agents`
- `jurisdictions`
- `domains`
- `issue_map`
- `key_findings`
- `sources`
- `comparison_matrix`
- `coverage_gaps`
- `error`

## Error Vocabulary

- `null`
- `mcp_unavailable`
- `partial_sources`
- `timeout`
- `classification_ambiguous`
- `classification_mismatch`
- `source_coverage_insufficient`
- `internal_error`

## Integrity Rules

- `meta_version`, `summary`, `active_profile`, and
  `orchestrator_route_mode` must be non-empty strings.
- `summary` must be substantive downstream metadata, not `None`, `TBD`, or a
  process placeholder. Keep it within 500 rough tokens.
- `jurisdictions` and `domains` must be non-empty lists of non-empty strings.
- `classification_warnings`, `co_running_agents`, and `key_findings` must be
  lists; when present, every item must be a non-empty string.
- For quality evaluation, every `key_findings[*]` item should cite at least one
  known `sources[*].id`.
- `research_mode` must be one of:
  - `general`
  - `game_regulation`
  - `game_plus_general`
  - `fallback`
- `mode_source` must be one of:
  - `orchestrator`
  - `self_classified`
- Every `issue_map[*].authority_ids` value must exist in `sources[*].id`.
- Every `issue_map[*].issue`, `issue_map[*].answer`, and
  `issue_map[*].authority_ids[*]` value must be a non-empty string.
- Every source grade must be one of `A`, `B`, `C`, or `D`.
- Every source must include non-empty `title`, `citation`, `pinpoint`, and
  `url_or_access`.
- If `research_mode` is `fallback`, `fallback_reason` should be non-null.
- If route and question visibly conflict, add `classification_mismatch` to
  `classification_warnings`.
- Every `coverage_gaps[*]` entry should include `type` and `description`.
- If `error` is non-null, include a matching `coverage_gaps` entry explaining
  the issue.
- Fallback results must include at least one `coverage_gaps` entry.
- When `comparison_matrix` is used, each row should include non-empty `issue`,
  one non-empty cell per compared jurisdiction, and non-empty `status`.

## Coverage Gap Types

- `classification_mismatch`
- `source_coverage`
- `source_access`
- `jurisdiction`
- `specialist_handoff`
- `temporal_status`
- `other`
- `claim_verification`

## Quality Relationship

Passing this output contract is necessary but not sufficient. A schema-valid
result can still fail the legal-quality standard if it omits material issues,
uses weak authority for controlling propositions, or hides unresolved source
limits. Apply `legal-output-quality-standard.md` and `quality-check.md` before
delivery.

## Optional Claim Checks

`claim_checks` is optional and additive. When present, every claim check should
include:

- `claim_id`
- `issue_id`
- `claim`
- `authority_ids`
- `support_strength`
- `currentness`
- `confidence_impact`
- `limitation`

`support_strength` must be one of `direct`, `indirect`, `background`, or
`unsupported`. Every `authority_ids[*]` value must exist in `sources[*].id`.
Apply `claim-verification-loop.md` before finalizing this field.

## Optional Output Mode

`output_mode` is optional and additive. Existing readers ignore it. When
present, it must be one of:

- `executive_brief`
- `comparative_matrix`
- `enforcement_case_law`
- `black_letter_commentary`
- `canonical` (default; equivalent to omitting the field)

Optional companion fields:

- `output_mode_audience`: free-text audience descriptor (e.g. `C-suite`,
  `compliance team`, `litigation lead`).
- `output_mode_format`: one of `markdown`, `docx_ready`, or `docx`.
  When `docx`, the deliverable is generated via `scripts/render-docx.py`
  on top of `docx_ready_markdown` packaging.

Apply `skills/output-mode-composition.md` whenever a non-`canonical`
mode is selected for a standalone deliverable. The orchestrator-compatible
`legal-research-agent-result.md` is unchanged regardless of `output_mode`.

## Result Memo Structure

Apply `result-memo-composition.md` before writing the result file. When local
execution is available, run:

```bash
python3 scripts/check-result-structure.py {OUTPUT_DIR}
```

The result memo must expose the actual user question, short-answer source
anchoring, issue analysis, source IDs, confidence, limits, coverage gaps, and
handoff notes in the body. Metadata alone is not enough.
The `### Rule And Authority` subsection must visibly cite every authority source
ID used by the issue map.
When metadata `comparison_matrix` is non-empty, the result memo must include a
visible `## Comparison Matrix` table before `## Sources`.
The `## Sources` table must mirror metadata source `grade`, `title`,
`citation`, `pinpoint`, and `url_or_access` exactly for each source ID.
