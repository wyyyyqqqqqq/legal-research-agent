# Claim Verification Loop

Use this skill after source collection, source grading, and currentness checks,
but before final analysis and output composition.

The goal is to verify material legal propositions at the claim level, not only
at the memo or source-list level.

## Material Claims

Create claim checks for material propositions that support:

- the short answer;
- key findings;
- each issue's controlling rule;
- application of the rule to the user's facts;
- counter-analysis, caveats, or confidence limits.

Do not create a claim check for every sentence. Focus on propositions that would
change the answer, confidence, or practical next step if wrong.

## Metadata Shape

`claim_checks` is optional for compatibility. When present, use this shape:

```json
{
  "claim_checks": [
    {
      "claim_id": "claim_001",
      "issue_id": "issue_001",
      "claim": "The operator should verify terms-change notice obligations against official Korean authority.",
      "authority_ids": ["src_001"],
      "support_strength": "direct",
      "currentness": "checked",
      "confidence_impact": "supports_medium_or_high",
      "limitation": "Current official law should be checked before final reliance."
    }
  ]
}
```

Use `issue_001`, `issue_002`, and so on unless `issue_map[*].id` is available.

## Support Strength

Use these values:

- `direct`: source directly supports the proposition.
- `indirect`: source supports the proposition through a clear inference.
- `background`: source gives context but does not support a controlling legal
  proposition.
- `unsupported`: the proposition is not yet source-supported.

Only `direct` or clearly sufficient `indirect` support can carry a legal
conclusion. `background` and `unsupported` cannot support high confidence.

## Verification Steps

For each material claim:

1. Assign a stable `claim_id`.
2. Link it to the relevant issue.
3. State the claim in one sentence.
4. Attach one or more `authority_ids`.
5. Confirm each authority ID exists in `sources[*].id`.
6. Assign `support_strength`.
7. Record currentness status for the claim.
8. State any limitation or confidence impact.

## High-Confidence Rule

Do not mark an issue `high` confidence unless the issue has at least one
`direct` claim check, or the result explains why the issue is a direct verified
lookup.

If a high-confidence proposition is only `indirect`, `background`, or
`unsupported`, lower confidence or add a visible limitation.

## Key Finding Rule

Every source anchor used in `key_findings[*]` should be represented by at least
one claim check when `claim_checks` is present. Key findings are downstream
decision material, so they cannot float above the claim registry.

## Fallback Behavior

If a material claim cannot be verified:

- set `support_strength` to `unsupported` or `background`;
- lower the issue confidence;
- add a `coverage_gaps` entry with type `claim_verification` or
  `source_coverage`;
- use visible limiting language in the memo.

Do not hide failed claim verification in internal notes.
