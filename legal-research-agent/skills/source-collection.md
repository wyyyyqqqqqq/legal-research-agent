---
name: source-collection
description: Use for source planning and retrieval in all research modes — emits compact source envelopes and enforces source-layer minimums.
disable-model-invocation: true
---

# Source Collection

Use this skill for source planning and retrieval in all research modes.

Apply `jurisdiction-source-playbook.md` first when jurisdiction, legal hierarchy,
or source minimums are not obvious.

## Source Payload Envelope

Pass compact source records downstream. Do not inject full text by default.

```json
{
  "id": "src_001",
  "title": "Source title",
  "url": "https://example.gov/source",
  "issuer": "Regulator or court",
  "document_type": "statute|regulation|case|agency|secondary|mixed|other",
  "jurisdiction": "KR",
  "publication_date": "YYYY-MM-DD|null",
  "effective_date": "YYYY-MM-DD|null",
  "accessed_date": "YYYY-MM-DD",
  "language": "ko|en|ja|...",
  "source_authority": "primary|secondary|mixed",
  "grade": "A|B|C|D",
  "citation": "Article, section, paragraph, decision number",
  "pinpoint": "Specific pinpoint",
  "relevant_passages": [
    {
      "pinpoint": "Article 17(1)",
      "text": "sanitized excerpt",
      "word_count": 120
    }
  ],
  "summary": "60-120 word source-specific summary",
  "full_text_ref": "path-or-cache-key|null",
  "prompt_injection_risk": "low|medium|high",
  "prompt_injection_findings": [],
  "sanitizer_status": "passed|redacted|excluded",
  "temporal_status": "current|recently_amended|pending|not_yet_in_force|repealed|unknown",
  "temporal_note": null
}
```

## Token Discipline

- `relevant_passages[*].text`: target 100-250 words each.
- `relevant_passages`: target 1-3 passages per source per downstream task.
- `summary`: target 60-120 words.
- Do not pass `full_text` inline downstream unless a tool specifically needs it.
- Re-open full text only for targeted pinpoint verification.

## Korean Law Strategy

Prefer `korean-law` MCP when available:

1. Search law names and aliases.
2. Fetch law text and targeted articles.
3. Check delegated regulation structure when relevant.
4. Search precedents, administrative interpretations, and agency decisions.
5. Check annexes, forms, old/new comparisons, and article history when relevant.

Fallback order when MCP is unavailable:

1. Local cached official sources, if available and reasonably current.
2. Python/open-law scripts, if available in the host repo.
3. Official public source URLs.
4. General web search only as last resort, with lower confidence.

Record `mcp_unavailable` or `partial_sources` when Korean primary source coverage
is materially limited.

## EU Law Strategy

Prefer structured official EUR-Lex or regulator sources where available. Check
consolidated text, effective dates, and procedural status before treating an EU
instrument as current.

## Other Jurisdictions

Use official government, regulator, court, or gazette sources first. If only
secondary material is available, lower confidence and record the limitation.

## Source Minimum Enforcement

Before analysis, compare collected sources against the required source minimum:

- If the issue turns on statute plus delegated rule, collect both or record the
  missing layer.
- If the issue turns on procedure, collect the legal basis plus official
  procedure/form guidance where available.
- If the issue turns on sanctions, collect the legal basis plus official
  enforcement or penalty material where available.
- If the issue is comparative, collect jurisdiction-specific support before
  synthesis.

Do not fill a minimum-source gap with secondary commentary unless the result is
explicitly marked source-limited.

## Source-Layer Stop Condition

For `general` and general-law `game_plus_general` issues, apply
`general-law-source-playbook.md` before final analysis. Compare the collected
source envelopes against:

- `knowledge/general/domain-source-checklist.md`; and
- any active matching playbook from
  `knowledge/general/source-playbook-index.json`.

Do not proceed to high-confidence analysis when a required source layer is
missing, currentness is unknown for controlling authority, or a secondary source
is filling a primary-law role. Record the missing layer in `coverage_gaps` and
carry the confidence ceiling into the issue map.

## Document Conversion

For PDF, DOCX, PPTX, XLSX, HWP, or HWPX sources:

- convert to structured text only when the source is expected to be Grade A/B or
  materially important;
- sanitize extracted text;
- store full converted text behind a reference;
- pass only relevant excerpts downstream.

## Temporal Status Tags

Apply temporal tags to statutes, regulations, agency rules, and guidance:

- `[Recently Amended - YYYY-MM-DD]`
- `[Pending Amendment]`
- `[Not Yet In Force - effective YYYY-MM-DD]`
- `[Repealed - YYYY-MM-DD]`

Carry this into source metadata using `temporal_status` and `temporal_note`.
When structured source metadata is available, also apply
`skills/currentness-check.md` and populate `sources[*].currentness`.

Use `coverage_gaps` with type `temporal_status` when currentness cannot be
verified for a controlling source.

## Similar-Statute Guard

When two or more sources in the same jurisdiction regulate similar subject
matter, create a boundary table before analysis:

| Source | Section | Subject | Key Operative Language | Exception/Safe Harbor |
|---|---|---|---|---|

Use it to avoid conflating adjacent statutes, delegated rules, guidance, or
agency interpretations.
