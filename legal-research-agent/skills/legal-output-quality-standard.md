# Legal Output Quality Standard

Use this skill before writing `legal-research-agent-result.md`.

## Non-Negotiable Standard

The output must be useful to a legal professional. It should not merely summarize
search results. It must show:

- the legal issue;
- the controlling rule or best available authority;
- how the authority applies to the user's facts;
- limits, uncertainty, and counter-arguments;
- practical next steps or handoff points.

Token savings are irrelevant if any of these are missing for a material issue.

## Required Structure

For each material issue, include:

1. Issue label.
2. Short answer.
3. Controlling authority or best available source.
4. Application to facts.
5. Counter-analysis or limiting caveat.
6. Confidence.
7. Coverage gap, if any.

## Materiality

An issue is material when it could change:

- whether the client may proceed;
- launch timing;
- disclosure or filing obligations;
- regulator exposure;
- civil, administrative, or criminal risk;
- whether another specialist must be consulted.

Do not omit material issues to keep output short.

## Jurisdiction Handling

For multi-jurisdiction work:

- answer each requested jurisdiction separately;
- do not collapse member-state or state-level variation into a single broad
  statement;
- identify when a jurisdiction-specific rule is missing or unverified;
- synthesize only after jurisdiction-specific analysis.

## Authority Handling

- Use primary or official sources for controlling propositions where reasonably
  available.
- Attribute secondary sources transparently.
- Do not cite secondary commentary as "the law."
- Do not cite self-regulatory material as binding law unless an official source
  gives it legal effect.
- Mark stale, pending, repealed, or not-yet-effective law inline.
- Do not mark an issue `high` confidence when the result is fallback,
  source-limited, access-limited, jurisdiction-limited, temporally uncertain, or
  affected by a classification mismatch.

## Practicality

A strong result should tell the downstream writer or lawyer:

- what is likely required;
- what must be verified;
- what risk remains;
- what facts would change the answer;
- which specialist should handle any out-of-scope issue.

The practical next step must name a concrete action: verify a current source,
confirm a missing fact or jurisdiction, coordinate a specialist handoff, run
separate research, or build a comparison matrix. Do not end a legal memo with a
generic instruction to "handle appropriately."

## Failure Labels

Use explicit labels rather than smoothing over uncertainty:

- `[Unverified]`
- `[Unresolved Conflict]`
- `[Material Risk]`
- `[Source Coverage Gap]`
- `[Specialist Handoff]`

## Local Quality Gate

When a result directory exists, run:

```bash
python3 scripts/run-local-checks.py
python3 scripts/check-fixture-consistency.py
python3 scripts/check-knowledge-coverage.py
python3 scripts/check-result-structure.py {OUTPUT_DIR}
python3 scripts/evaluate-quality.py {OUTPUT_DIR} --case-spec {CASE_SPEC_JSON}
python3 scripts/evaluate-golden-set.py
python3 scripts/compare-token-runs.py {TOKEN_COMPARISON_MANIFEST_JSON}
```

The quality gate is intentionally stricter than schema validation.
`check-knowledge-coverage.py` also protects the agent instructions themselves:
core source-planning and jurisdiction markers must remain present. A result can
be well-formed JSON and still fail if it lacks source support, cites weak
authority for high-confidence conclusions, omits a required jurisdiction, or
misses a material issue term from the case spec.
It can also fail when metadata reports an error or material coverage gap while
issue confidence remains high, or when a metadata key finding lacks a source
anchor.

For multi-case evaluation, each quality spec must point to a stable `case_id`.
When `requires_comparison_matrix`, `required_co_running_agents`, or
`requires_privacy_handoff` is present, those checks are mandatory and cannot be
offset by token savings.

Token comparison is a separate evidence gate, not a quality substitute. Use
actual Claude Code `events.jsonl` files when available. Proxy metrics may be
recorded only as review data. A merged run that increases token usage must
record a concrete `quality_reason`; otherwise the token comparison fails. When
available, attach a `quality_report` to the token manifest so the comparison can
verify that `quality_status` and `case_id` match the quality gate output.
