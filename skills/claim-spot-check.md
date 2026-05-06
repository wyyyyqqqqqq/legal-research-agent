---
name: claim-spot-check
description: Use after source collection and before final analysis — guards against source laundering and unverified claims.
disable-model-invocation: true
---

# Claim Spot-Check and Source Laundering Guard

Use this skill after source collection and before final analysis.

## Purpose

Intercept:

- hallucinated legal anchors;
- wrong statute/article numbers;
- stale effective dates;
- secondary-source interpretations presented as primary law;
- phantom citations to primary sources that were not fetched;
- paraphrases of primary law without pinpoint verification.

## When to Run

Run for all normal research. You may skip only when:

- the task is a simple quick lookup; and
- the answer is single-jurisdiction; and
- every controlling source was directly confirmed from an official primary
  source.

## Claim Registry

Track material claims:

```json
{
  "claim": "Game operators must disclose probabilities for paid randomized items.",
  "anchor": "Game Industry Promotion Act Article ...",
  "source_ids": ["src_001"],
  "status": "Verified|Unverified|Contradicted",
  "priority": "high|medium|low",
  "notes": "Pinpoint verified against official source."
}
```

For output-level claim verification, use `claim-verification-loop.md` and carry
material checks into optional `claim_checks` metadata when feasible.

## Source Laundering Patterns

Flag laundering when:

1. a secondary source states an interpretation as though it were the law;
2. a source references a primary authority that was not fetched;
3. a memo paraphrases a statute without pinpoint citation;
4. a secondary summary is cited as if it were a regulator decision;
5. the analysis relies on an official-looking but non-official mirror.

## Required Actions

- `Contradicted`: correct before proceeding.
- `Unverified` high-priority claim: fetch primary source if possible.
- Source laundering: fetch the primary source, re-attribute to secondary
  commentary, or mark `[Unverified]`.
- Do not allow a high-confidence conclusion to rely solely on an unresolved
  laundering-flagged source.

## Metadata

Unresolved issues should appear in `coverage_gaps`, for example:

```json
{
  "type": "claim_verification",
  "description": "Penalty threshold could not be verified from an official source."
}
```
