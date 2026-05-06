# Golden-Set Evaluation

Run each case through legacy and merged profiles. Local deterministic fixtures
exercise the merged-agent quality gates before any human or LLM-as-judge review.

## Candidate Cases

1. KR general legal research question.
2. KR loot-box/probability item regulation.
3. Japan game company launching in Korea.
4. Game + consumer protection + advertising question.
5. Game + data-protection spotting question with a data-protection specialist
   running in parallel where appropriate.
6. Korean game company launching in the EU, game regulation only.

## Local Golden-Set Fixtures

The current deterministic fixture set covers:

| Case id | Route pattern | Required quality focus |
|---|---|---|
| `kr_general_basic` | `general-only` | KR jurisdiction, terms-change notice, official-source verification |
| `kr_loot_box_probability` | `game-only` | probability disclosure, enforcement/sanction coverage |
| `jp_kr_game_launch` | `multi-jurisdiction game` | KR/JP separation and `comparison_matrix` |
| `game_consumer_advertising` | `game-only` | influencer advertising and limited package consumer notices |
| `game_data_protection_handoff` | `game + specialist handoff` | explicit privacy handoff and co-running specialist ownership |
| `classification_mismatch_general_to_game` | `routing edge case` | route preservation plus explicit `classification_mismatch` |
| `fallback_source_coverage` | `fallback` | conservative source-limited output with fallback reason |

## Mandatory Criteria

- Quality criteria are mandatory. Token savings cannot compensate for a failed
  quality criterion.
- Result and metadata files exist.
- Metadata validates.
- Metadata text fields are substantive: no empty or placeholder `summary`,
  route fields, jurisdictions, domains, issue labels, issue answers, authority
  IDs, or key-finding items. `summary` must stay within 500 rough tokens.
- No fabricated sources.
- Each key legal conclusion maps to at least one source.
- Each `key_findings[*]` item cites at least one known source ID.
- Confidence is conservative: fallback, error, source/access/jurisdiction,
  temporal-status, and classification-mismatch gaps cannot pair with high
  issue confidence.
- No critical legal issue found by legacy or reviewer is omitted.
- Required jurisdictions are not omitted.
- Game cases cover relevant taxonomy categories.
- `research_mode`, `mode_source`, and route metadata are populated.
- Duplicate merged-agent dispatch does not occur.
- Token usage is reported from events where available.

## Deterministic Local Quality Gate

Before human or LLM-as-judge review, run:

```bash
python3 scripts/run-local-checks.py
python3 scripts/check-fixture-consistency.py
python3 scripts/check-knowledge-coverage.py
python3 scripts/check-citation-auditor-vendor.py
python3 scripts/check-citation-auditor-smoke.py
python3 scripts/validate-output.py /path/to/output
python3 scripts/check-result-structure.py /path/to/output
python3 scripts/evaluate-quality.py /path/to/output --case-spec /path/to/case-quality-spec.json
python3 scripts/evaluate-golden-set.py
python3 scripts/compare-token-runs.py /path/to/token-comparison-manifest.json
```

`run-local-checks.py` is the repeatable local preflight and can write a JSON
report with `--report`. `check-fixture-consistency.py` prevents drift between
case fixtures, quality specs, and golden-set output directories.
`check-knowledge-coverage.py` prevents accidental thinning of core research
instructions and jurisdiction source maps. `check-citation-auditor-vendor.py`
prevents the vendored citation-auditor skill, verifier set, and Python utility
package from silently disappearing or drifting from the pinned vendor stamp.
`check-citation-auditor-smoke.py` verifies the deterministic local
chunk/aggregate/render path against a legal research result fixture without
calling live verifier subagents.
`validate-output.py` checks the contract shape. `check-result-structure.py`
checks that the result memo exposes question, route context, issue blocks,
analysis, sources, coverage gaps, and handoff notes. `evaluate-quality.py`
checks minimum legal-quality signals such as source support, Grade A/B support
for high-confidence conclusions, no D-grade legal basis, jurisdiction coverage,
confidence alignment for fallback/error/coverage-gap outputs, and case-specific
material issue terms. It also checks that metadata key findings cite known
source IDs. `evaluate-golden-set.py` applies those checks across every
`tests/fixtures/quality/*-quality-spec.json` file and fails if any expected
output directory is missing. `compare-token-runs.py` turns Phase 2 token
evidence into a route-pattern report and blocks token increases that lack a
documented quality reason.

Source detail integrity is mandatory:

- every metadata source must include non-empty `title`, `citation`, `pinpoint`,
  and `url_or_access`;
- every metadata source must appear in the result `## Sources` table;
- the table's `Grade`, `Title`, `Citation`, `Pinpoint`, and `Access` cells must
  match metadata for the same source ID, with `Access` mirroring
  `sources[*].url_or_access`.

Question fidelity is mandatory. The result memo's `## Question` section must be
substantive. In local golden-set fixtures, it must match the case fixture
`user_question` exactly so that evaluation does not drift away from the prompt
being tested.

Analysis structure is mandatory. The result memo's `## Analysis` section must
include non-empty subsections in this order:

- `### Rule And Authority`
- `### Application`
- `### Counter-Analysis Or Caveat`
- `### Practical Next Step`

`### Rule And Authority` must display every authority source ID used by
`issue_map[*].authority_ids`. Source IDs appearing only in metadata, issue
blocks, or the source table are not enough for the rule paragraph.

`### Practical Next Step` must be substantive and action-oriented. It must tell
the next operator what to verify, ask, confirm, coordinate, hand off, separately
research, or compare. Generic closure such as "handle appropriately" and
placeholder values such as `TBD` fail the golden-set gate.

Coverage gap display is mandatory. The result memo's `## Coverage Gaps` section
must not be empty. When metadata `coverage_gaps` is non-empty, the visible
section must not say `None` and must display each gap `type` in readable form
such as `source coverage` or `classification mismatch`.

Handoff display is mandatory. The result memo's `## Handoff Notes` section must
not be empty. When metadata `co_running_agents` is non-empty, the visible
section must not say `None`; it must name every co-running agent and include
handoff or delegation language.

Short answer source anchoring is mandatory. The result memo's `## Short Answer`
section must be substantive and, when metadata sources exist, cite at least one
metadata source ID. Fallback, error, or coverage-gap outputs must show limiting
language in the short answer. Specialist handoff outputs must name the
co-running owner and use handoff or delegation language in the short answer.

Issue block field integrity is mandatory. Every `### Issue` block must carry
its own non-empty `Answer`, `Sources`, `Confidence`, and `Limits` lines. Game
research modes must also include a non-empty `Taxonomy` line in every issue
block. The issue block's `Confidence` value must match the corresponding
`issue_map[*].confidence`, and every `issue_map[*].authority_ids` value must
appear in that block's `Sources` line.

Case specs may require route-specific gates:

- `requires_comparison_matrix` for multi-jurisdiction comparison cases;
- `required_co_running_agents` for specialist handoff cases;
- `requires_privacy_handoff` when game-law output must not duplicate detailed
  privacy analysis.
- `required_classification_warnings` for route/question mismatch cases;
- `expected_error` and `expected_fallback_reason` for fallback or partial
  failure cases.
- `required_coverage_gap_types` for cases where an error or fallback must leave
  a structured gap trail.
- `required_taxonomy` for game-regulation cases that must preserve issue
  taxonomy coverage.

When `requires_comparison_matrix` is true, `comparison_matrix` must be a
non-empty list of object rows. Each row must include:

- non-empty `issue`;
- one non-empty cell for every `required_jurisdictions` value;
- non-empty `status` describing whether the row is verified, tentative, or
  requires current-source checking.

When metadata `comparison_matrix` is non-empty, the result memo must also show
a `## Comparison Matrix` markdown table before `## Sources`. The visible table
must display each row's issue, every compared jurisdiction cell, and status.

## Quality-First Rule

Default switching is blocked if merged mode:

- omits a material legal issue;
- omits a required jurisdiction;
- weakens citation integrity;
- relies on secondary commentary as though it were primary law;
- fails to verify current law for a controlling proposition;
- handles a specialist issue superficially instead of handing it off.

This remains true even if merged mode uses substantially fewer tokens.

## Optional Rubric

Score 0-10:

- source quality
- issue spotting
- jurisdiction coverage
- practical usefulness
- metadata completeness

Suggested pass line:

- average score at least 8;
- no mandatory criterion fails;
- no critical issue omission.

## Token Reporting Table

Use `scripts/measure-prompt-footprint.py` for Phase 0 prompt/instruction
footprint diagnostics; the current Phase 0 snapshot is recorded in
`docs/prompt-footprint.md`. Use `scripts/measure-tokens.py` for actual Claude
Code `events.jsonl` usage whenever legacy and merged runs are available. Use
`scripts/compare-token-runs.py` to compare those measurements by route pattern.
The comparison manifest must keep quality status visible because token savings
cannot compensate for a failed legal-quality gate.

| Route pattern | Legacy measured tokens | Merged measured tokens | Delta | Decision |
|---|---:|---:|---:|---|
| `general-only` | TBD | TBD | TBD | TBD |
| `game-only` | TBD | TBD | TBD | TBD |
| `game-plus-general` | TBD | TBD | TBD | TBD |
| `game-plus-data-protection` | TBD | TBD | TBD | TBD |

Minimal token-comparison manifest shape:

```json
{
  "version": "1.0",
  "required_route_patterns": ["general-only"],
  "patterns": [
    {
      "case_id": "kr_general_basic",
      "route_pattern": "general-only",
      "quality_status": "pass",
      "quality_report": "quality-reports/kr_general_basic.json",
      "legacy": {"events": ["legacy-general.events.jsonl"]},
      "merged": {"events": ["merged-general.events.jsonl"]}
    }
  ]
}
```

If `merged` has a positive `total_billed_like` delta, add `quality_reason` or
the comparison gate fails. If either side lacks actual `events`, proxy metrics
may be recorded, but the decision remains proxy-only review data.
When `quality_report` is present, its `status` and `case_id` must match the
manifest entry so token evidence cannot drift away from the quality gate result.
Use `required_route_patterns` to make a comparison manifest fail when a planned
route-pattern baseline is accidentally omitted.
When both sides report `agent_calls`, the comparison report includes an
`agent_calls` delta. If merged uses more agent calls than legacy, add
`agent_call_reason` or the gate fails.
Proxy metrics can include `agent_calls`, `result_bytes`, and `wall_clock_ms`.
`agent_calls` may be supplied either top-level or inside `proxy_metrics`; if both
are present they must match. Positive `result_bytes` or `wall_clock_ms` deltas
are warnings, not hard rollout blockers.
The JSON report includes a top-level `summary` with decision counts, aggregate
actual-token totals, aggregate token delta, proxy-only pattern count, and
aggregate agent-call delta.
