# Source Grading

Use this skill whenever adding a source to metadata.

## Grades

### Grade A

Use for controlling or near-controlling sources:

- statutes
- regulations
- enforcement decrees
- official regulator guidance
- official court decisions
- official agency decisions

### Grade B

Use for strong but not strictly controlling sources:

- official explanatory notes
- regulator press releases
- official FAQs
- respected practitioner guides that cite primary law

### Grade C

Use for secondary support:

- law firm articles
- academic commentary
- practitioner commentary
- reputable news analysis

Grade C can help discover issues or provide context. It should not alone support
a high-confidence legal conclusion.

### Grade D

Use for unreliable or non-authoritative material:

- unsourced web commentary
- marketing pages
- AI summaries with no citations
- anonymous posts

Do not cite Grade D for legal propositions.

## Metadata Fields

Each source should include:

```json
{
  "id": "src_001",
  "title": "Official source title",
  "grade": "A",
  "citation": "Article, paragraph, decision number, or section",
  "pinpoint": "Specific pinpoint",
  "url_or_access": "URL, database path, MCP source, or access note"
}
```

Use stable source IDs and reference them from `issue_map[*].authority_ids`.
`url_or_access` is required and must also be displayed in the result memo's
`## Sources` table as the `Access` cell.

## Korean and Translation Refinements

- Official Korean statutes, enforcement decrees, enforcement rules, agency
  notices, and official decisions are normally Grade A.
- Unofficial translations of statutes are Grade B maximum and must point back to
  the original-language source.
- Self-regulatory bodies may be Grade B or C depending on official recognition;
  mark them with `[Industry Self-Regulatory Body]` when material.
- Secondary commentary that quotes primary law is still secondary unless the
  primary source was independently fetched and verified.

## Source Laundering

Downgrade or flag a source when:

- it presents interpretation as primary law;
- it cites a primary source that was not fetched;
- it paraphrases legal text without pinpoint citation;
- it is an unofficial mirror that looks official.

No high-confidence conclusion may rely solely on a laundering-flagged source.
