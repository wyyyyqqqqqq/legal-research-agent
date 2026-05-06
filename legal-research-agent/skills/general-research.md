# General Legal Research

Use this skill in `general` mode and as the general-law portion of
`game_plus_general`.

## Research Steps

1. Identify the jurisdiction(s).
2. Identify the legal domain(s).
3. State the requested deliverable: quick answer, research memo, issue list,
   comparison, or handoff note.
4. Apply `trust-boundary.md` before using external text.
5. Apply `jurisdiction-source-playbook.md` to create jurisdiction profiles and
   source minimums.
6. Apply `general-law-source-playbook.md` to select domain source layers from
   `knowledge/general/domain-source-checklist.md` and any active playbook in
   `knowledge/general/source-playbook-index.json`.
7. Apply `source-collection.md` to collect compact source envelopes.
8. Prefer primary and official sources.
9. Run claim spot-checking unless the answer is a directly verified simple
   lookup.
10. Record source limitations explicitly.
11. Build an issue map where each issue points to source IDs.

## Quick Mode

Use quick mode only when:

- the question is single-jurisdiction;
- the issue is a narrow lookup;
- no synthesis or counter-analysis is required; and
- the answer can be confirmed from one or two official sources.

If confirmation fails, switch back to the full workflow.

## Korean Law

When available, prefer `korean-law` MCP for:

- statutes and enforcement decrees
- official amendments
- court or agency decisions
- official regulator guidance

If the MCP is unavailable, set `error` to `mcp_unavailable` or
`partial_sources` when the limitation matters, and record a `coverage_gaps`
entry.

## Non-Korean Law

Use official sources where possible:

- statutes and regulations from official government databases
- regulator guidance
- court databases
- official agency decisions

If only secondary sources are available, lower confidence and state that the
answer requires confirmation against primary law.

## Jurisdiction Discipline

For every jurisdiction:

- build a separate source plan before synthesis;
- identify the legal hierarchy that controls the answer;
- select the general-law domain checklist or active source playbook before
  source collection;
- check currentness where statutes, regulations, or agency rules are material;
- avoid jurisdiction blending in multi-jurisdiction questions;
- use `coverage_gaps` for missing state, member-state, delegated-rule, or agency
  coverage.

For US questions, do not answer at "US law" level when state law controls. For
EU questions, do not treat directives or member-state implementation as a single
undifferentiated rule. For Korean questions, check delegated rules and
supplementary provisions before final conclusions.

## Output Expectations

- Keep the research focused on the user's question.
- Do not expand into game-specific issues unless the facts require it.
- Separate black-letter law, guidance, enforcement practice, and practical
  recommendations.
- Include counter-analysis or limiting authority for material conclusions.
- Mark unverified or source-limited claims rather than smoothing them over.
- Do not mark a general-law issue `high` confidence when its selected domain
  source layers or active source playbook minimums were not checked.
