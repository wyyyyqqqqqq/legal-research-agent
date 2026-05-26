# Glossary Schema

This reference defines the JSON shape for jurisdiction-aware legal glossary
files produced by `skills/specialists/glossary-manager.md`.

Glossaries are translation-memory and definition controls. They do not replace
source research and must not introduce definitions that lack source support.

## Use When

Use the schema when:

- a Korean, foreign-language, or technical legal term materially affects the
  answer;
- the same term appears repeatedly and translation consistency matters;
- a term has multiple plausible translations depending on context;
- a memo needs a definition table, appendix, or downstream drafting handoff;
- the user asks for terminology management, glossary work, or translation
  memory.

Do not create a glossary entry for ordinary English words or for legal
definitions that are not source-backed.

## File Naming

Write glossary files under:

```text
output/glossary/glossary-{jurisdiction-code}.json
```

Examples:

```text
output/glossary/glossary-kr.json
output/glossary/glossary-us.json
output/glossary/glossary-eu.json
```

Use uppercase jurisdiction codes inside the JSON object, matching the
jurisdiction vocabulary used elsewhere in the agent (`KR`, `US`, `EU`, `JP`,
`UK`, or a more specific code where the research requires it).

## Top-Level Object

Required shape:

```json
{
  "schema_version": "1.0",
  "jurisdiction": "KR",
  "language_pair": "ko-en",
  "last_updated": "2026-05-26",
  "terms": []
}
```

Fields:

| Field | Required | Type | Rule |
|---|---:|---|---|
| `schema_version` | Yes | string | Must be `"1.0"` until the schema changes. |
| `jurisdiction` | Yes | string | Use the controlling jurisdiction code. |
| `language_pair` | Yes | string | Use `{source}-{target}`, such as `ko-en` or `ja-en`. |
| `last_updated` | Yes | string | ISO date when the glossary was last changed. |
| `terms` | Yes | array | List of term entries. |

## Term Entry Fields

Each entry in `terms` must follow this shape:

```json
{
  "term": "시행령",
  "source_language": "ko",
  "preferred_translation": "Enforcement Decree",
  "definition": "A delegated presidential decree that implements a statute.",
  "authority_ids": ["src_001"],
  "pinpoints": ["Act title or article pinpoint"],
  "status": "verified",
  "notes": "Use for 대통령령-level implementing decrees.",
  "context_rules": []
}
```

Field rules:

| Field | Required | Type | Rule |
|---|---:|---|---|
| `term` | Yes | string | Original-language term exactly as used in the source. |
| `source_language` | Yes | string | ISO-style language code such as `ko`, `en`, `ja`. |
| `preferred_translation` | Yes | string | Default translation for this jurisdiction and context. |
| `definition` | Yes | string | Source-backed explanation, not an invented paraphrase. |
| `authority_ids` | Yes | array | One or more source IDs from the research metadata. |
| `pinpoints` | Yes | array | Article, section, paragraph, page, or official heading. |
| `status` | Yes | string | `verified`, `provisional`, or `deprecated`. |
| `notes` | No | string | Usage caveats, mistranslation risks, or drafting guidance. |
| `context_rules` | Yes | array | Context-specific translation overrides. Empty array allowed. |

Allowed `status` values:

| Status | Meaning |
|---|---|
| `verified` | Supported by primary or official source and fit for reuse in the same scope. |
| `provisional` | Useful but incomplete; needs confirmation before high-stakes reliance. |
| `deprecated` | Retained for history or migration; do not use as the default translation. |

## Context Rule Fields

Use `context_rules` when a term needs a different translation in a specific
setting. Do not overwrite the default translation merely because one memo needs
a narrower usage.

Shape:

```json
{
  "when": "financial-data special-law context",
  "translation": "Special Credit Information Act",
  "authority_ids": ["src_004"],
  "pinpoints": ["Article ..."],
  "note": "Use only when the sector-specific statute controls."
}
```

Fields:

| Field | Required | Rule |
|---|---:|---|
| `when` | Yes | Describe the factual or legal context that triggers the rule. |
| `translation` | Yes | Context-specific translation. |
| `authority_ids` | Yes | Source IDs supporting the context rule. |
| `pinpoints` | Yes | Pinpoint support for the context distinction. |
| `note` | No | Drafting or scope warning. |

## Authority and Pinpoint Rules

- Every term entry must have at least one `authority_id`.
- Every authority ID must appear in the run metadata or source appendix.
- Every definition must have a pinpoint unless the source genuinely lacks
  internal numbering; in that case identify the official heading or page.
- Secondary sources may explain usage but should not be the sole basis for a
  high-confidence legal definition when primary or official sources exist.
- If only secondary support exists, mark the entry `provisional`.

## Korean Starter Glossary

For Korean law, load or create entries for these starter terms before adding new
ones:

| Korean term | Default English translation | Mistranslation risk |
|---|---|---|
| 법률 | Act / statute | Do not translate every 법 as "law" when a statutory tier matters. |
| 시행령 | Enforcement Decree | Distinguish 대통령령 from ministerial rules. |
| 시행규칙 | Enforcement Rule | Usually ministry-level implementing rule. |
| 고시 | Notice / public notice | Can be binding or procedural depending on authority. |
| 판결 | Judgment / court decision | Choose based on posture. |
| 의뢰인 | Client | Avoid "requester" in legal-service context. |
| 당사자 | Party | Context may be litigation or contract. |
| 과태료 | Administrative fine | Not a criminal fine. |
| 벌금 | Criminal fine | Distinguish from 과태료 and 과징금. |
| 과징금 | Administrative surcharge / penalty surcharge | Often regulatory, not criminal. |
| 가명정보 | Pseudonymized information | Do not translate as anonymized information. |
| 개인정보처리자 | Personal information controller | Use the statutory term where privacy law controls. |
| 정보주체 | Data subject | Privacy-law term. |
| 법인 | Juridical person / corporation | Pick contextually; do not assume business corporation. |
| 법률자문 | Legal advice / legal consultation | Avoid implying attorney-client relationship unless facts support it. |

Starter entries still need source IDs and pinpoints in the actual JSON file.

## Validation Rules

A glossary file is invalid if:

- `schema_version`, `jurisdiction`, `language_pair`, or `terms` is missing;
- a term lacks `authority_ids` or `pinpoints`;
- a term uses a status outside `verified`, `provisional`, or `deprecated`;
- the same `term` appears twice without context-rule differentiation;
- a context rule lacks source support;
- a definition is based only on translation preference rather than legal source
  support;
- a Korean legal-tier term collapses statute, decree, rule, and notice into one
  undifferentiated translation.

## Example

```json
{
  "schema_version": "1.0",
  "jurisdiction": "KR",
  "language_pair": "ko-en",
  "last_updated": "2026-05-26",
  "terms": [
    {
      "term": "과태료",
      "source_language": "ko",
      "preferred_translation": "Administrative fine",
      "definition": "A non-criminal monetary administrative sanction.",
      "authority_ids": ["src_010"],
      "pinpoints": ["Administrative sanction provision"],
      "status": "verified",
      "notes": "Do not translate as criminal fine.",
      "context_rules": []
    }
  ]
}
```

## Quality Checklist

- [ ] The glossary uses the correct jurisdiction and language pair.
- [ ] Every definition is backed by a source ID and pinpoint.
- [ ] Context-specific translations are captured as `context_rules`.
- [ ] Provisional entries are clearly marked.
- [ ] Deprecated entries are not used as defaults.
- [ ] Korean legal-tier terms preserve hierarchy distinctions.
- [ ] The glossary does not introduce legal conclusions beyond the sources.
