---
name: analysis-issue-structuring
description: Use after source collection and claim spot-checking — turns sources into structured evidence cards and an issue map.
disable-model-invocation: true
---

# Analysis and Issue Structuring

Use this skill after source collection and claim spot-checking.

For comparative analysis across jurisdictions, apply
`references/comparative-framework.md`. For counter-analysis on
material conclusions, apply `references/counter-analysis-checklist.md`.

## Evidence Cards

Use compact evidence cards as the default analysis input:

```json
{
  "source_id": "src_001",
  "grade": "A",
  "jurisdiction": "KR",
  "issue_tags": ["randomized_rewards", "consumer_protection"],
  "pinpoint": "Article ...",
  "verified_claim": "Probability disclosure obligation applies to ...",
  "limits": "Confirm current enforcement guidance.",
  "temporal_status": "current"
}
```

Avoid bulk-pasting full source text. Re-open full text only when a pinpoint must
be verified.

## Issue Tree

Build an issue tree:

1. threshold applicability;
2. controlling rule;
3. exceptions or safe harbors;
4. procedure or disclosure form;
5. enforcement/remedies;
6. open questions or coverage gaps.

For comparisons, build this tree per jurisdiction before writing synthesis.

For specialist handoffs, keep the issue in the tree but mark:

- what this agent can answer;
- what the specialist owns;
- what facts or sources the specialist needs;
- how the handoff affects the practical recommendation.

## Counter-Analysis Requirement

For every material conclusion, include at least one:

- counter-argument;
- limiting authority;
- alternative interpretation;
- enforcement caveat;
- fact pattern that could change the answer.

If no meaningful counterpoint exists, say so briefly and explain why the risk
appears low.

## Conflict Handling

When sources conflict:

- prefer higher legal hierarchy;
- prefer more recent current law over stale law;
- distinguish statute, delegated rule, guidance, enforcement practice, and
  secondary commentary;
- mark unresolved conflicts explicitly instead of forcing a false synthesis.

## Korean Law Notes

For Korean law:

- check supplementary provisions before concluding effective dates;
- distinguish law, enforcement decree, enforcement rule, notice, guideline, and
  agency interpretation;
- preserve Korean legal terms where translation could blur meaning;
- add glossary notes for terms that materially affect the answer.

## Output Mapping

Every issue in `issue_map` should include:

- a concise legal answer;
- authority IDs;
- confidence;
- known limits or coverage gaps when confidence is not high.
