# Case Briefs Reference Pack

Detailed case-brief framework for `skills/specialists/case-briefs.md`. Load
this pack when drafting, tailoring, or quality-checking a case brief or judicial
opinion summary.

This pack is a briefing framework. It does not supply case law and does not
replace reading the opinion.

## Quick Start

1. Confirm the opinion text, court, date, and procedural posture.
2. Extract facts without legal characterization.
3. Frame issues as precise questions.
4. State narrow holdings before broader principles.
5. Separate reasoning, dicta, concurrence, and dissent.
6. Mark missing or uncertain fields rather than inferring.

## Intake

| Item | Required | Notes |
|---|---:|---|
| Full opinion text | Yes | Include page, paragraph, or slip-opinion citations where available. |
| Court and jurisdiction | Yes | Identify trial, appellate, supreme, constitutional, administrative, or foreign court. |
| Decision date | Yes | Use exact date from the opinion. |
| Citation / docket | If available | Include reporter, neutral citation, docket, or case number. |
| Procedural posture | Yes | Appeal, certiorari, motion, trial judgment, administrative review, etc. |
| Questions user cares about | If provided | Use to prioritize significance, not to distort the holding. |

## Case Metadata

```text
Case name:
Court:
Jurisdiction:
Date:
Citation / docket:
Judge / panel:
Lower court or agency:
Procedural posture:
Disposition:
Opinion types:
```

If a field is absent from the source, write `Not stated`.

## Procedural Posture

Capture:

- how the case reached the court;
- lower-court or agency result;
- motion or review vehicle;
- standard or scope of review if the court states it;
- what issues are properly before the court.

Do not treat background litigation history as holding or reasoning.

## Fact Extraction

Separate facts:

| Fact type | Include | Exclude |
|---|---|---|
| Background facts | Context needed to understand the dispute | Colorful but legally irrelevant narrative |
| Material facts | Facts the court relied on for the holding | Advocate assertions not adopted by the court |
| Procedural facts | Filings, orders, rulings, review posture | Unrelated docket events |
| Disputed facts | Facts the court identifies as contested | Speculation from party briefing |

Every material fact should be traceable to a page, paragraph, or section.

## Issues Presented

Write issues as:

```text
Whether [legal standard] applies when [material facts].
```

Rules:

- one issue per question;
- match the court's framing when available;
- avoid overbroad issues that erase procedural posture;
- separate statutory, constitutional, procedural, and evidentiary questions.

## Holding and Disposition

Use this table:

| Issue | Narrow holding | Broader rule, if any | Disposition | Pinpoint |
|---|---|---|---|---|
| | | | affirmed / reversed / vacated / remanded / dismissed / other | |

Rules:

- State the narrow holding first.
- Identify the disposition separately from the reasoning.
- If the court announces a broader principle, label it as broader rule.
- Do not elevate dicta into holding.

## Reasoning and Rule Extraction

For each issue, capture:

| Element | Notes |
|---|---|
| Rule or test applied | Quote exact language when the standard matters. |
| Authorities relied on | Cases, statutes, regulations, constitutional provisions. |
| Analytical steps | Court's sequence of reasoning. |
| Application to facts | How facts satisfy or fail the rule. |
| Limiting language | Facts, posture, jurisdiction, or scope limits. |

Use direct quotations sparingly but precisely for standards, tests, and legally
operative phrases.

## Dicta and Limiting Language

Flag:

- statements unnecessary to the result;
- broad policy observations;
- hypothetical examples;
- discussion of issues not before the court;
- narrow fact-dependent limitations;
- procedural limitations that affect precedential value.

If uncertain whether a statement is dicta, write `possible dicta` and explain
why.

## Concurring and Dissenting Opinions

| Opinion | Author | Agreement / disagreement | Key reasoning | Practical significance |
|---|---|---|---|---|
| Concurrence | | | | |
| Dissent | | | | |

Rules:

- Do not blend concurrence or dissent into the majority holding.
- Identify plurality or fragmented opinions if present.
- Note when a concurrence controls under jurisdiction-specific doctrine only if
  supported by the source or reliable authority.

## Significance

Address only significance supported by the opinion and the user's research
context:

- new rule or clarified test;
- application of existing rule to new facts;
- split creation or resolution;
- statutory interpretation method;
- procedural or evidentiary implication;
- compliance, litigation, or transactional relevance.

Avoid unsupported predictions about future litigation.

## Output Quality Checklist

- [ ] Caption, court, date, and posture are complete or marked `Not stated`.
- [ ] Material facts are separated from background and procedural facts.
- [ ] Issues are precise and posture-aware.
- [ ] Narrow holdings precede broad principles.
- [ ] Disposition is separate from holding.
- [ ] Legal standards are quoted when wording matters.
- [ ] Dicta and limiting language are flagged.
- [ ] Concurrences and dissents are not treated as majority holdings.
- [ ] Missing source details are not invented.

## Pitfalls

- Rewriting a party's argument as the court's holding.
- Treating remand instructions as a final merits holding.
- Overstating precedential value from a procedural disposition.
- Omitting the standard of review.
- Summarizing facts in advocacy tone.
- Ignoring fragmented opinions.
- Using a secondary case summary when the full opinion is available.
