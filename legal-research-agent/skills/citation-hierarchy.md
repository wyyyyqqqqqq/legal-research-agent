# Citation Hierarchy and Failure Handling

Use this skill when preparing the result memo and metadata.

## Citation Hierarchy

1. Primary: statute, regulation, case, agency decision, official guidance.
2. Secondary: academic or practitioner commentary.
3. Excluded as sole basis: blogs, wiki-style summaries, marketing pages,
   unsupported AI summaries.

## Citation Codes

- `[P#]`: legislation or regulation
- `[T#]`: treaty or convention
- `[C#]`: case law or decision
- `[A#]`: administrative document or agency guidance
- `[S#]`: secondary source

Within each citation type, order by reliability grade first. Grade A sources
should receive the lowest numbers.

## Special Tags

- `[Industry Self-Regulatory Body]`
- `[Unverified]`
- `[Unresolved Conflict]`
- `[Material Risk]`
- `[Recently Amended - YYYY-MM-DD]`
- `[Pending Amendment]`
- `[Not Yet In Force - effective YYYY-MM-DD]`
- `[Repealed - YYYY-MM-DD]`

Place temporal and risk tags at the specific finding they qualify. Do not hide
them only in a footnote or summary.

## Failure Handling

- Ambiguous user scope: ask concise clarifying questions when necessary; otherwise
  proceed with explicit assumptions.
- Source collection failure: retry with a different strategy, then record
  `partial_sources`.
- MCP unavailable: use fallback sources and record `mcp_unavailable` if material.
- Contradicted anchor: correct and loop back to targeted source collection once.
- Source laundering: fetch primary source, re-attribute transparently, or mark
  `[Unverified]`.
- Quality check failure: remediate once. If still unresolved, mark the issue
  rather than hiding the failure.

All unresolved findings must remain explicit and traceable.
