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
- No fabricated sources.
- Each key legal conclusion maps to at least one source.
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
and case-specific material issue terms. `evaluate-golden-set.py` applies those
checks across every
`tests/fixtures/quality/*-quality-spec.json` file and fails if any expected
output directory is missing.

Source detail integrity is mandatory:

- every metadata source must include non-empty `title`, `citation`, `pinpoint`,
  and `url_or_access`;
- every metadata source must appear in the result `## Sources` table;
- the table's `Grade`, `Title`, `Citation`, and `Pinpoint` cells must match
  metadata for the same source ID.

Analysis structure is mandatory. The result memo's `## Analysis` section must
include non-empty subsections in this order:

- `### Rule And Authority`
- `### Application`
- `### Counter-Analysis Or Caveat`
- `### Practical Next Step`

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

| Route pattern | Legacy measured tokens | Merged measured tokens | Delta | Decision |
|---|---:|---:|---:|---|
| `general-only` | TBD | TBD | TBD | TBD |
| `game-only` | TBD | TBD | TBD | TBD |
| `game-plus-general` | TBD | TBD | TBD | TBD |
| `game-plus-data-protection` | TBD | TBD | TBD | TBD |
