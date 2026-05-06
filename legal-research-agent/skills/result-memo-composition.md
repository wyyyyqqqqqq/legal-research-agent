# Result Memo Composition

Use this skill when writing `legal-research-agent-result.md`.

The result memo is the research artifact that downstream legal-writing and human
review rely on. It must be more than a search summary.

## Required Sections

Write these sections in this order:

1. `# Legal Research Result`
2. `## Question`
3. `## Route Context`
4. `## Short Answer`
5. `## Issues`
6. `## Analysis`
7. `## Sources`
8. `## Coverage Gaps`
9. `## Handoff Notes`

`Handoff Notes` may say `None.` when there is no specialist handoff.

## Question

Copy the actual user question into `## Question`. Do not leave this section
empty, shorten it to `TBD`, or replace it with an internal route label. Local
golden-set fixtures must match their case fixture `user_question` exactly.

## Route Context

The `## Route Context` section must mirror metadata exactly:

- `Active profile` = `active_profile`
- `Orchestrator route mode` = `orchestrator_route_mode`
- `Research mode` = `research_mode`
- `Mode source` = `mode_source`
- `Co-running agents` = `co_running_agents` in the same order, or `[]` when
  empty

## Short Answer

Write a substantive short answer, not `None`, `TBD`, or a generic process note.
When metadata has sources, cite at least one `src_*` anchor in the short answer.
When the output is fallback, error-bearing, or has `coverage_gaps`, include
visible limiting language such as source-limited, coverage gap, fallback,
unverified, conservative, insufficient, or needs verification. When
`co_running_agents` is non-empty, name the specialist owner and use handoff or
delegation language in the short answer.

## Issue Blocks

Under `## Issues`, create one `### Issue` block for each material issue.

Each issue block must include non-empty values for:

- `Answer`
- `Sources`
- `Confidence`
- `Limits`

When `research_mode` is `game_regulation` or `game_plus_general`, every issue
block must also include a non-empty `Taxonomy` line. If an issue is a general
law issue inside `game_plus_general`, state that boundary explicitly rather
than omitting the field.

Every source listed in an issue block must exist in
`legal-research-agent-meta.json` under `sources[*].id`.
Every `issue_map[*].authority_ids` source must appear in the matching issue
block's `Sources` line.
Every issue block's `Confidence` value must match the matching
`issue_map[*].confidence` value. Put confidence caveats in `Limits`, not inside
the `Confidence` value.

## Analysis Requirements

The `## Analysis` section must include these subsections in this order, and
none may be empty:

1. `### Rule And Authority`
2. `### Application`
3. `### Counter-Analysis Or Caveat`
4. `### Practical Next Step`

Together these subsections should cover:

- controlling rule or best available authority;
- application to the user's facts;
- counter-analysis, caveat, or limiting fact;
- currentness or effective-date note where relevant;
- claim-verification limitation where a material proposition is only
  background-supported or unsupported;
- practical next step.

`### Rule And Authority` must cite source IDs for every authority source used
by the issue blocks. If `issue_map[*].authority_ids` includes `src_001` and
`src_002`, both IDs must appear in `### Rule And Authority`, not only in the
source table or metadata.

`### Practical Next Step` must be action-oriented, not generic closing prose.
Name the concrete follow-up: verify a current source, confirm a missing fact or
jurisdiction, coordinate a specialist handoff, run separate research, or build a
comparison matrix. Do not use vague text such as "handle appropriately" or
placeholder values such as `TBD`.

For multi-jurisdiction work, analyze each jurisdiction first and synthesize only
after jurisdiction-specific rows or paragraphs are complete.
When the metadata uses `comparison_matrix`, every matrix row must have a clear
issue label, one non-empty cell for each compared jurisdiction, and a status
such as verified, tentative, or requires current-source checking.
When `comparison_matrix` is non-empty, add a visible `## Comparison Matrix`
markdown table before `## Sources`. The table must display every metadata row's
`issue`, every compared jurisdiction cell, and `status`.

## Source Table

The `## Sources` section must include a table:

| ID | Grade | Title | Citation | Pinpoint | Access |
|---|---|---|---|---|---|

Use the same source IDs as metadata. Do not invent display-only IDs that are
absent from metadata.
Every metadata source must appear exactly once in the table, with the same grade
as `sources[*].grade`.
The table's `Title`, `Citation`, `Pinpoint`, and `Access` cells must exactly
mirror `sources[*].title`, `sources[*].citation`, `sources[*].pinpoint`, and
`sources[*].url_or_access`; do not leave any source-detail cell blank.

## Coverage Gaps

Do not hide gaps in prose. Use the section even when there are no gaps:

- `None identified from the collected sources.`

When gaps exist, include:

- missing jurisdiction or source layer;
- why it matters;
- impact on confidence;
- what would resolve it.
- currentness, effective-date, pending-amendment, stale-source, or supersession
  limitations when any controlling source has unresolved temporal status.

The displayed gap should include the metadata gap type in readable form, for
example `source coverage gap` for `source_coverage` or `classification mismatch
coverage gap` for `classification_mismatch`.

## Handoff Notes

Use this section for:

- privacy/data-protection specialist ownership;
- IP, tax, finance, employment, or other specialist boundaries;
- unresolved facts needed by another specialist.

If a specialist is co-running, name every `co_running_agents` owner, use visible
handoff or delegation language, and state what this agent did not analyze in
detail.

## Forbidden Shortcuts

- Do not leave template placeholders such as `{{short_answer_with_source_anchor}}`.
- Do not cite source IDs in the result that are absent from metadata.
- Do not put all uncertainty only in metadata.
- Do not collapse issue analysis into a single unstructured paragraph.
- Do not let `## Route Context` drift from metadata.
