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

## Route Context

The `## Route Context` section must mirror metadata exactly:

- `Active profile` = `active_profile`
- `Orchestrator route mode` = `orchestrator_route_mode`
- `Research mode` = `research_mode`
- `Mode source` = `mode_source`
- `Co-running agents` = `co_running_agents` in the same order, or `[]` when
  empty

## Issue Blocks

Under `## Issues`, create one `### Issue` block for each material issue.

Each issue block should include:

- `Answer`
- `Sources`
- `Confidence`
- `Taxonomy` for game-regulation issues
- `Limits`

Every source listed in an issue block must exist in
`legal-research-agent-meta.json` under `sources[*].id`.
Every `issue_map[*].authority_ids` source must appear in the matching issue
block's `Sources` line.

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
- practical next step.

For multi-jurisdiction work, analyze each jurisdiction first and synthesize only
after jurisdiction-specific rows or paragraphs are complete.
When the metadata uses `comparison_matrix`, every matrix row must have a clear
issue label, one non-empty cell for each compared jurisdiction, and a status
such as verified, tentative, or requires current-source checking.

## Source Table

The `## Sources` section must include a table:

| ID | Grade | Title | Citation | Pinpoint |
|---|---|---|---|---|

Use the same source IDs as metadata. Do not invent display-only IDs that are
absent from metadata.
Every metadata source must appear exactly once in the table, with the same grade
as `sources[*].grade`.
The table's `Title`, `Citation`, and `Pinpoint` cells must exactly mirror
`sources[*].title`, `sources[*].citation`, and `sources[*].pinpoint`; do not
leave any source-detail cell blank.

## Coverage Gaps

Do not hide gaps in prose. Use the section even when there are no gaps:

- `None identified from the collected sources.`

When gaps exist, include:

- missing jurisdiction or source layer;
- why it matters;
- impact on confidence;
- what would resolve it.

## Handoff Notes

Use this section for:

- privacy/data-protection specialist ownership;
- IP, tax, finance, employment, or other specialist boundaries;
- unresolved facts needed by another specialist.

If a specialist is co-running, name the specialist owner and state what this
agent did not analyze in detail.

## Forbidden Shortcuts

- Do not leave template placeholders such as `{{short_answer}}`.
- Do not cite source IDs in the result that are absent from metadata.
- Do not put all uncertainty only in metadata.
- Do not collapse issue analysis into a single unstructured paragraph.
- Do not let `## Route Context` drift from metadata.
